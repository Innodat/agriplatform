# Boabab WireGuard operator guide

This guide changes access to the existing host in place. It does not activate
applications, run migrations/imports, invite accounts or alter the Mac Mini or its
Tailscale network. Never recreate the server or regenerate its existing SSH keys.
Use the Hetzner console and the retained restricted public SSH session throughout
setup. The tests use command fakes; a successful test is not a live connectivity claim.

## Address and credential plan

Check operator LAN, WSL, Docker and server routes for overlap first. An example
allocation is server `10.77.80.1`, operator WSL `10.77.80.2`, CI `10.77.80.3` in an
otherwise unused `10.77.80.0/24`. The server uses `Address = 10.77.80.1/24` so newly
registered peers have a return route without restarting the interface. Every client
uses its own `/32` address and `AllowedIPs = 10.77.80.1/32`; clients get no subnet,
DNS, internet or peer-to-peer routing. Use only public IPv4 UDP51820 as the endpoint.
Server peer AllowedIPs are also individual `/32`s in this one server subnet.

Use MTU1200 persistently on the server, each human profile and the CI runner. Live
verification found that MTU1280 allowed the WireGuard handshake and TCP/SSH banner
but lost larger default SSH key-exchange packets; a server route MTU1200/MSS1160
restored normal SSH. This tunnel carries IPv4 only, so MTU1200 is intentional.
Preserve default SSH key exchange and strict host verification. Set the interface
MTU on both ends instead of relying on a temporary route override, and retest a
fresh default SSH connection after restart.

Each device has its own VPN key and SSH key. Human devices generate their own
WireGuard private keys and transfer only public keys to the administrator. The
server CLI never generates client private keys. CI has a separate VPN identity and
separate deployment SSH key. A VPN key permits network reachability; an SSH key
and Unix account still control login and privilege. Do not share human VPN keys,
add new humans to sudo/docker groups, or copy the administrator's key for CI.

## Prepare the existing host

In the protected operational Terraform workspace retain the existing state and set:

```hcl
server_name          = "boabab"
wireguard_enabled    = true
public_ssh_enabled   = true
private_ssh_verified = false
```

Inspect the saved plan: only the name and UDP51820 rule may change. Reject any
replacement, server ID/disk/IP/resource-address or user_data change. TCP443 stays
public; TCP22 stays restricted to the approved administrator CIDRs. Apply only that
reviewed plan. From the trusted session set `sudo hostnamectl set-hostname boabab`.
No cloud-init editing or reexecution is needed.

Install Ubuntu's `wireguard-tools` and `nftables` on the existing host with the
operator's normal package process. Create `/etc/wireguard` root-owned mode0700.
Create `/etc/wireguard/wg0.conf` once, root-owned mode0600, with this structure:

```ini
[Interface]
PrivateKey = <SERVER_PRIVATE_KEY_GENERATED_ON_SERVER>
Address = 10.77.80.1/24
ListenPort = 51820
MTU = 1200
```

Generate the server key using `wg genkey` with stdout captured directly into a
root-only file/config under umask077, never terminal output, shell tracing, command
arguments or a tracked directory. Do not replace an existing server key on rerun.
Show only its public key with `wg pubkey < /etc/wireguard/server-private.key` if a
protected key file was used. Remove an extra private key copy after constructing
and verifying the protected config. An existing config must match this documented
format before using `peers.py`: only PrivateKey, Address, ListenPort and optional
MTU (1200–1420); every peer must have a unique identity marker, PublicKey and one
AllowedIPs address. SaveConfig, hooks, Endpoint and unmanaged peers are rejected.

Prevent forwarding explicitly, including when Docker has enabled system-wide
forwarding. Do not disable forwarding globally and break Docker. Add an independent
nftables table, preserving all existing rules (never `flush ruleset`):

```nft
table inet boabab_wg {
  chain ssh_input {
    type filter hook input priority -200; policy accept;
    iifname "wg0" ip saddr 10.77.80.0/24 tcp dport 22 accept
    iifname "wg0" drop
  }
  chain no_forward {
    type filter hook forward priority -200; policy accept;
    iifname "wg0" drop
    oifname "wg0" drop
  }
}
```

Save this root-owned mode0600 as `/etc/wireguard/no-forward.nft`. Install this
root-owned mode0755 helper as `/usr/local/sbin/boabab-wg-firewall`:

```sh
#!/bin/sh
set -eu
if /usr/sbin/nft list table inet boabab_wg >/dev/null 2>&1; then
  {
    printf '%s\n' 'delete table inet boabab_wg'
    cat /etc/wireguard/no-forward.nft
  } | /usr/sbin/nft -f -
else
  /usr/sbin/nft -f /etc/wireguard/no-forward.nft
fi
```

The delete-and-create batch commits atomically and touches only `boabab_wg`; an
invalid replacement leaves the previous table intact. Never flush the ruleset or
Docker's tables. Ensure only this unit manages `boabab_wg`. Install root-owned
mode0644 `/etc/systemd/system/boabab-wg-firewall.service`:

```ini
[Unit]
Description=Boabab WireGuard SSH-only isolation
Before=wg-quick@wg0.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/sbin/boabab-wg-firewall
ExecReload=/usr/local/sbin/boabab-wg-firewall

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/wg-quick@wg0.service.d/` and put this root-owned mode0644
file at `require-firewall.conf` inside it:

```ini
[Unit]
Requires=boabab-wg-firewall.service
After=boabab-wg-firewall.service
```

From the independent console/public administrative session:

```sh
sudo systemctl daemon-reload
sudo systemctl enable boabab-wg-firewall.service wg-quick@wg0.service
sudo systemctl start boabab-wg-firewall.service
sudo systemctl start wg-quick@wg0.service
sudo nft list table inet boabab_wg
```

Use `sudo systemctl reload boabab-wg-firewall.service` for atomic rule updates.
Stopping/restarting the required firewall service can stop dependent wg0 and does
not guarantee it starts again. After a firewall restart explicitly run
`sudo systemctl start wg-quick@wg0.service`, check both units and test private SSH
again from an independent administrator path. The service deliberately leaves its
isolation table installed on stop. Do not enable a distribution nftables service
that flushes Docker's rules. Verify both units, table and isolation after reboot.
The example permits only SSH input on wg0; this is independent of per-peer
WireGuard authentication. Any additional host INPUT rules must permit UDP51820
and TCP22 on wg0; do not broadly open other services.
WireGuard itself changes no forwarding setting and is never an exit node.

Start and persist the existing interface with
`sudo systemctl enable --now wg-quick@wg0`. Confirm `sudo wg show wg0 public-key`,
`sudo wg show wg0 listen-port`, `ip address show wg0`, and its connected subnet
route. Never print `wg showconf`, `wg show all dump` or config contents into logs:
those can include private keys. Retain public SSH during all these steps.

## Onboard a device and Unix account

On the device, install a WireGuard client; on WSL install `wireguard-tools` inside
WSL and confirm its own network namespace supports it. Under umask077 run
`wg genkey > <PRIVATE_KEY_FILE>` and `wg pubkey < <PRIVATE_KEY_FILE> > <PUBLIC_KEY_FILE>`
in a protected non-repository directory. A GUI client may generate its own key
instead. Transfer only the public key. Register one identity per device:

```sh
sudo python3 <CHECKOUT>/platform/deployment/wireguard/peers.py add alex-laptop \
  --address 10.77.80.4/32 --public-key '<DEVICE_PUBLIC_KEY>'
```

The CLI requires the interface to be running and serializes changes with a bounded
lock. It validates the entire embedded registry, writes atomically with mode0600,
and syncs only wg0. Identical add/remove retries are safe and resync the saved
state. A failed sync restores the previous config and attempts live restoration;
if that also fails it explicitly reports that console recovery is required. Do not
run concurrent manual edits or `wg-quick save`, which bypass these protections.

Install this profile on that device, keeping its private key local:

```ini
[Interface]
PrivateKey = <THIS_DEVICE_PRIVATE_KEY>
Address = 10.77.80.4/32
MTU = 1200

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <EXISTING_PUBLIC_IPV4>:51820
AllowedIPs = 10.77.80.1/32
PersistentKeepalive = 25
```

Create the person's separate unprivileged Unix account and install their SSH public
key through the retained administrative connection, for example:

```sh
sudo adduser --disabled-password --gecos '' alex
sudo install -d -m 700 -o alex -g alex /home/alex/.ssh
sudo install -m 600 -o alex -g alex <REVIEWED_AUTHORIZED_KEYS_FILE> /home/alex/.ssh/authorized_keys
```

The reviewed authorized_keys file must prefix each human key with these options,
which retain interactive PTY access while denying agent, TCP/socket and X11 forwarding:

```text
no-agent-forwarding,no-port-forwarding,no-X11-forwarding ssh-ed25519 <PUBLIC_KEY> alex-laptop
```

For an existing account, append only the reviewed new public key with those options; do not overwrite
other authorized devices. No sudo/docker membership is granted. Privilege increases
require an explicit separate administrator decision. Copy the existing host's
ED25519 public key from the trusted console into the device's known_hosts under
`10.77.80.1`. Do not trust an unauthenticated ssh-keyscan result. Configure an SSH
alias `boabab` with HostName `10.77.80.1`, that person's User and IdentityFile, and
StrictHostKeyChecking yes. Test `ssh boabab id` from the actual device/WSL namespace.
Verify it reaches only the intended host and that human privilege matches policy.

For offboarding, run `peers.py remove alex-laptop`, remove the corresponding SSH
public key from the person's authorized_keys, and verify both access paths are
revoked. For complete offboarding revoke all their device peers/SSH keys, expire
the account (`sudo usermod --expiredate 1 alex`) and terminate its active sessions
(`sudo loginctl terminate-user alex`). Do not delete business files as part of
access revocation. Removing a peer alone does not revoke Unix credentials or an
existing public-SSH session; removing an SSH key alone leaves VPN reachability.

## Configure and verify CI

Generate the dedicated CI WireGuard and SSH keys in a protected operator context,
transfer only the VPN public key to the server CLI as `github-production` with
`10.77.80.3/32`, and put private material directly into GitHub production environment
secrets. Never commit keys, put them in Terraform or upload them as artifacts.
Register a distinct CI SSH public key for the existing root-capable deployment
account. `restrict` in authorized_keys disables forwarding/PTY while preserving
ordinary command/SCP access; it does not restrict the commands root can execute.
The current coordinator needs root filesystem/Docker authority. A limited Unix
account is not a working substitute. A forced-command wrapper requires its own
review and is not supplied by this tooling.

Configure these secrets alongside the existing release credentials:

| Secret | Value |
| --- | --- |
| WG_CLIENT_PRIVATE_KEY | Dedicated CI WireGuard private key, canonical 32-byte base64 |
| WG_SERVER_PUBLIC_KEY | Existing server WireGuard public key, canonical 32-byte base64 |
| WG_ENDPOINT | Existing public IPv4 followed by `:51820` |
| WG_SERVER_ADDRESS | `10.77.80.1/32` |
| WG_CLIENT_ADDRESS | `10.77.80.3/32` |
| DEPLOY_HOST | `10.77.80.1` exactly |
| DEPLOY_USER | Root-capable deployment account, currently `root` |
| SSH_PRIVATE_KEY | Separate CI deployment SSH private key |
| SSH_KNOWN_HOSTS | Independently verified existing host-key entry for `10.77.80.1` |

Main-only production jobs remain serialized. Early validation rejects malformed
keys, addresses, endpoint or mismatched host without remote effects. Immediately
before deployment, the runner installs the tools, creates a root-only temporary
config and an ownership-marked interface, adds exactly the server `/32` route, and
verifies strict SSH authentication/host identity with the harmless `true` command.
Only then does the unchanged migration/release flow run. Always-run teardown deletes
only that owned interface/config; deletion failure attempts to bring the verified owned interface down and remove
its private route, still erases private key files and retains ownership/route
metadata for retry. It reports incomplete cleanup until interface deletion succeeds.
An unowned interface is never modified. SSH deployment files use a separate temporary
directory. No credentials are included in artifacts or command error messages.

Before enabling automatic application releases, manually dispatch
`.github/workflows/wireguard-connectivity.yml` from main. It uses the protected
production environment and the same `platform-production` concurrency group as
releases; it only installs tools, validates inputs, sets up the tunnel (including
strict `ssh ... true`) and always tears it down. It performs no application release,
migration or publication. Restrict that environment to protected main. Do not trigger the full production release solely to test
VPN connectivity while bootstrap approval remains pending. Capture non-secret
success/failure and SSH fingerprint evidence, including teardown after a forced
setup/SSH failure. Retain public TCP22 until this CI test and real administrator
private SSH both pass. Then, only with working Hetzner console recovery, explicitly
set `private_ssh_verified=true`, `public_ssh_enabled=false` and inspect/apply the
firewall-only plan. The assertion is an operator decision, not automatic detection.

## Rotate credentials without losing administrator access

Keep a separately verified administrator credential/device and console or restricted
public SSH session open throughout rotation. Never rotate the only working VPN and
SSH credentials together. Generate each replacement human private key on its own
device and transfer only public keys. Use a temporary distinct peer identity and
unused address in the server /24 (the CLI rejects replacing an identity in place).
Install the replacement profile, test private SSH, and only then remove the old
peer. If verification fails, retain the old peer/profile and revoke the failed new
peer; retry through the independent administrative path. For human SSH rotation,
append the new public key with the same no-forwarding options, test a fresh login
using that explicit key, then remove the old key by its exact fingerprint. Do not
replace authorized_keys wholesale or assume an existing session tests the new key.

For CI rotation, hold automatic production releases and drain queued runs, waiting
for active releases to finish; never cancel an in-flight migration. Keep the
connectivity workflow available. GitHub concurrency serializes workflows but does
not serialize operator secret edits, so change no secrets during an active job.
Create a replacement CI peer at an unused /32 with a new identity, and update
WG_CLIENT_PRIVATE_KEY and WG_CLIENT_ADDRESS together while jobs are held. For SSH
rotation, first add the new dedicated public key to the deployment account, then
update SSH_PRIVATE_KEY. Keep the previous peer/key and secret material protected
outside logs for this bounded verification window. Run the main-only connectivity
workflow with the new inputs. On success revoke the old peer and SSH key, erase
retired private copies and release the hold. On failure restore the previous
secrets together, verify connectivity, and remove the failed replacement peer/key.
Never leave overlapping keys indefinitely.

Changing the server VPN key requires coordinated replacement of WG_SERVER_PUBLIC_KEY
and each human profile; schedule it with the same release hold and an independent
console/public path. Back up the protected server config, replace only its key,
restart wg0, update clients and verify them. If verification fails, restore the
previous protected server config/key and matching client/server-public-key secrets,
then restart and retest. Do not regenerate SSH host keys as part of VPN rotation.

## Lost deployment SSH session

Deployment SSH uses ServerAliveInterval=15 and ServerAliveCountMax=3 to bound
silent transport failure. A lost SSH connection does not prove the remote migration
or release stopped, rolled back or completed. Hold new releases and reconnect
through the independent administrator path. Inspect the remote process and host
release lock, the attempt's evidence.json and actual owner migration histories;
wait for or reconcile any still-running operation. Follow the main deployment
README's partial-release recovery procedure with the original source/digests.
Do not blindly rerun the workflow, cancel migrations or reverse applied SQL.

## Console recovery

If private access fails, use the Hetzner web console on the same server. Verify
`sshd -t`, `systemctl is-active ssh`, interface address/routes, WireGuard public key
and UDP port, and the independent isolation table. Do not generate new SSH/server
VPN keys, loosen host verification or create a replacement host.

Restore restricted public SSH from the protected Terraform workspace by setting
`public_ssh_enabled=true`, `private_ssh_verified=false` and `admin_cidrs` to the
operator's current public `/32`. Inspect a firewall-only plan and apply it; keep
UDP51820 and HTTPS443. If emergency console/provider firewall repair is necessary,
allow TCP22 only from that exact administrator `/32` and reconcile Terraform state
and config afterward. Verify public SSH using the original host key before further
repair. Never open TCP22 to `0.0.0.0/0` or `::/0`.

For failed peer synchronization, the saved config is restored to its prior state;
a live rollback failure means runtime state is unknown. Through the console,
validate the protected saved config and recover with
`sudo systemctl restart wg-quick@wg0`, which disconnects VPN users temporarily and
reloads the persistent peer registry/routes. For a crash between atomic save and
live sync, rerun the intended identical add/remove to converge or restart after
inspection. Confirm revoked peers remain absent after restart. Restore a protected
previous config only after assessing which newer peer changes it would undo.
Keep public fallback until administrator and CI private checks pass again.

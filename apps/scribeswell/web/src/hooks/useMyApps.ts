/** Public reading is independent of current protected app discovery. */
import {useCurrentApps} from '@platform/ui-business';
import {appDirectoryClient} from '@/lib/app-directory';
import {useAuth} from '@/context/AuthContext';
export function useMyApps(){
  const {session,loading}=useAuth();
  return useCurrentApps(appDirectoryClient,session?{accountId:session.user.id,accessToken:session.access_token}:null,loading);
}

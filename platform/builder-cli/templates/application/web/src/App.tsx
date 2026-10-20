// Create-once owner seed: presentational shell only.
export function App() {
 return <><a className="skip-link" href="#main">Skip to content</a><header><span className="brand">{{OWNER}}</span><nav aria-label="Main"><a href="/" aria-current="page">Home</a></nav></header><main id="main" tabIndex={-1}><h1>Welcome</h1><p>Your application starts here.</p></main></>;
}

import { PetPlayground } from "./pet-playground";

const features = [
  ["Commit-powered growth", "Every unseen GitHub commit earns XP. Level requirements rise as your companion grows."],
  ["Food with meaning", "Each new commit has a deterministic 20% chance to drop food. Syncing twice never duplicates rewards."],
  ["Lives on your desktop", "Let your pet nap below the menu bar, walk along the screen, relax in its cage, or disappear with one switch."],
  ["Private by design", "No keylogging, telemetry, source-code reading, or token in save data. You decide exactly when GitHub syncs."],
];

export default function Home() {
  return (
    <main>
      <nav className="nav shell" aria-label="Main navigation">
        <a className="brand" href="#top"><span className="brand-mark">C</span> CodePet</a>
        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#connect">Connect GitHub</a>
          <a className="pill small" href="https://github.com/Cyn30/codepet" target="_blank" rel="noreferrer">View source</a>
        </div>
      </nav>

      <section className="hero shell" id="top">
        <div className="hero-copy">
          <div className="eyebrow"><span /> Your commits have a heartbeat</div>
          <h1>Keep coding.<br/><em>Raise a friend.</em></h1>
          <p className="lede">An original desktop companion that naps, wanders, plays, and grows with your real GitHub progress.</p>
          <div className="hero-actions">
            <a className="pill" href="#install">Adopt your CodePet</a>
            <a className="text-link" href="#playground">Meet the pets <span>→</span></a>
          </div>
          <div className="trust-row">
            <span>MIT licensed</span><span>No keylogging</span><span>Local save</span>
          </div>
        </div>
        <PetPlayground />
      </section>

      <section className="marquee" aria-label="Available pet breeds">
        <div>RAGDOLL <b>✦</b> DEVON REX <b>✦</b> GOLDEN SHADED <b>✦</b> GOLDEN RETRIEVER <b>✦</b> GERMAN SHEPHERD <b>✦</b> SCOTTISH COLLIE</div>
      </section>

      <section className="section shell" id="features">
        <div className="section-head">
          <div><span className="kicker">BUILT FOR CONSISTENCY</span><h2>A habit tracker<br/>you can care about.</h2></div>
          <p>CodePet turns invisible progress into a tiny life on your desktop—without watching your keyboard or reading your code.</p>
        </div>
        <div className="feature-grid">
          {features.map(([title, description], index) => (
            <article className="feature-card" key={title}>
              <span className="feature-number">0{index + 1}</span>
              <div className={`mini-icon icon-${index + 1}`} aria-hidden="true" />
              <h3>{title}</h3><p>{description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="life-section" id="playground">
        <div className="shell life-grid">
          <div className="life-copy">
            <span className="kicker">A REAL LITTLE ROUTINE</span>
            <h2>From project kickoff<br/>to a life well lived.</h2>
            <p>Choose a lifespan that matches a course, product milestone, thesis, or long-term practice. Fourteen days is the minimum—because care should have time to become a habit.</p>
            <ul className="checks"><li>Increasing XP curve</li><li>Gentle rest days</li><li>Pet memories, never deletion</li></ul>
          </div>
          <div className="timeline-card">
            <div className="timeline-top"><span>BYTE&apos;S JOURNEY</span><strong>Day 42 / 365</strong></div>
            <div className="timeline-line"><i style={{width: "22%"}} /></div>
            <div className="milestones"><span className="done"><b>1</b>Tiny Sprout</span><span><b>4</b>Explorer</span><span><b>10</b>Companion</span><span><b>20</b>Legend</span></div>
            <blockquote>“Today I found a snack in your commit. I saved you the best crumb.”</blockquote>
          </div>
        </div>
      </section>

      <section className="section shell connect" id="connect">
        <div className="section-head compact">
          <div><span className="kicker">PRIVATE GITHUB SETUP</span><h2>Connect in two minutes.</h2></div>
          <p>Your password and token never enter CodePet’s save file. The in-app GitHub connection is the recommended sign-in method.</p>
        </div>
        <div className="steps">
          <article><span>1</span><h3>Open CodePet Home</h3><p>Select <b>Connect GitHub</b>. CodePet copies a one-time code and opens GitHub in your browser.</p></article>
          <article><span>2</span><h3>Approve read-only access</h3><p>Enter the one-time code on GitHub, approve the requested access, and return to CodePet.</p></article>
          <article><span>3</span><h3>Sync when you choose</h3><p>Right-click your pet and select <b>Sync GitHub</b>. That is the only time the API is queried.</p></article>
        </div>
        <details className="token-guide">
          <summary>Using GitHub CLI or a private fine-grained token instead?</summary>
          <div><p>Developers can run <code>gh auth login</code>. Alternatively, create a fine-grained token in GitHub Developer settings, select only the repositories you want counted, and grant read-only repository access. Then launch CodePet from the same terminal:</p><code>export GITHUB_TOKEN=&quot;github_pat_your_token_here&quot;</code><p>Never commit or paste a real token into a website, Issue, or source file. Revoke it immediately if exposed.</p></div>
        </details>
      </section>

      <section className="install" id="install">
        <div className="shell install-inner">
          <div><span className="kicker light">OPEN SOURCE · PUBLIC ALPHA</span><h2>Your next commit<br/>could bring home a friend.</h2></div>
          <div className="install-box"><code>pip install -e &quot;.[desktop]&quot;</code><code>codepet-desktop</code><a className="pill cream" href="https://github.com/Cyn30/codepet#readme" target="_blank" rel="noreferrer">Read the full guide</a></div>
        </div>
      </section>

      <footer className="shell footer"><a className="brand" href="#top"><span className="brand-mark">C</span> CodePet</a><p>Original art. Local-first. Made for people who keep showing up.</p><span>MIT · Public alpha</span></footer>
    </main>
  );
}

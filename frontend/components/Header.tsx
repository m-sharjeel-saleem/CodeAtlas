import { Github, Hexagon } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-bg/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5">
        <div className="flex items-center gap-2.5">
          <div className="relative grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-accent to-accent-cyan shadow-glow">
            <Hexagon className="h-5 w-5 text-white" strokeWidth={2.2} />
          </div>
          <div className="leading-tight">
            <div className="text-[15px] font-semibold tracking-tight text-white">CodeAtlas</div>
            <div className="text-[11px] text-zinc-500">Agentic codebase intelligence</div>
          </div>
        </div>

        <nav className="flex items-center gap-1 text-sm">
          <a
            href="#features"
            className="hidden rounded-lg px-3 py-2 text-zinc-400 transition-colors hover:text-white sm:block"
          >
            Features
          </a>
          <a
            href="https://github.com/m-sharjeel-saleem/CodeAtlas"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-zinc-300 transition-colors hover:bg-white/5 hover:text-white"
          >
            <Github className="h-4 w-4" />
            <span className="hidden sm:inline">Star on GitHub</span>
          </a>
        </nav>
      </div>
    </header>
  );
}

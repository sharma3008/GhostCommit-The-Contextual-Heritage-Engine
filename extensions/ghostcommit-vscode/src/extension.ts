import * as vscode from "vscode";

type GhostCommitConfig = {
  apiBaseUrl: string;
  apiToken: string;
  repoOwner: string;
  repoName: string;
};

function getConfig(): GhostCommitConfig {
  const cfg = vscode.workspace.getConfiguration("ghostcommit");
  return {
    apiBaseUrl: cfg.get<string>("apiBaseUrl", "http://127.0.0.1:8000"),
    apiToken: cfg.get<string>("apiToken", ""),
    repoOwner: cfg.get<string>("repoOwner", "sharma3008"),
    repoName: cfg.get<string>("repoName", "GhostCommit-The-Contextual-Heritage-Engine"),
  };
}

async function pingHealth(apiBaseUrl: string): Promise<boolean> {
  const base = apiBaseUrl.replace(/\/$/, "");
  const url = `${base}/health`;
  const res = await fetch(url, { method: "GET" });
  return res.ok;
}

function extractPrNumber(text: string): number | null {
  // Matches PR-101 or pr-101
  const match = text.match(/\bPR-(\d+)\b/i);
  if (!match) {
    return null;
  }

  const n = Number(match[1]);
  return Number.isInteger(n) && n > 0 ? n : null;
}

async function fetchContext(
  apiBaseUrl: string,
  apiToken: string,
  owner: string,
  repo: string,
  pr: number
): Promise<any> {
  const base = apiBaseUrl.replace(/\/$/, "");
  const url = new URL(`${base}/context`);
  url.searchParams.set("owner", owner);
  url.searchParams.set("repo", repo);
  url.searchParams.set("pr", String(pr));

  const headers: Record<string, string> = {};
  if (apiToken.trim()) {
    headers["Authorization"] = `Bearer ${apiToken}`;
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers,
  });

  if (!res.ok) {
    throw new Error(`Context API returned ${res.status}`);
  }

  return res.json();
}

function buildHoverMarkdown(data: any, prNumber: number): vscode.MarkdownString {
  const md = new vscode.MarkdownString(undefined, true);
  md.isTrusted = false;

  const title = data?.pull_request?.title ?? `PR ${prNumber}`;
  const state = data?.pull_request?.state ?? "unknown";
  const author = data?.pull_request?.author ?? "unknown";
  const summary = data?.rationale_summary?.content ?? "No summary available yet.";

  md.appendMarkdown(`**GhostCommit**\n\n`);
  md.appendMarkdown(`**PR #${prNumber}** — ${title}\n\n`);
  md.appendMarkdown(`- **State:** ${state}\n`);
  md.appendMarkdown(`- **Author:** ${author}\n\n`);
  md.appendMarkdown(`**Summary**\n\n`);
  md.appendText(summary);

  return md;
}

export function activate(context: vscode.ExtensionContext) {
  console.log("GhostCommit extension activated");

  const testCommand = vscode.commands.registerCommand("ghostcommit.test", async () => {
    const { apiBaseUrl, apiToken } = getConfig();

    try {
      const ok = await pingHealth(apiBaseUrl);

      if (!ok) {
        vscode.window.showErrorMessage(
          `GhostCommit Test failed: /health returned non-OK at ${apiBaseUrl}`
        );
        return;
      }

      const tokenStatus = apiToken.trim() ? "set" : "not set";
      vscode.window.showInformationMessage(
        `GhostCommit Test OK ✅ API: ${apiBaseUrl} (token: ${tokenStatus})`
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      vscode.window.showErrorMessage(
        `GhostCommit Test error: could not reach ${apiBaseUrl}/health — ${msg}`
      );
    }
  });

  const hoverProvider = vscode.languages.registerHoverProvider(
    { scheme: "file" },
    {
      async provideHover(document, position) {
        const range = document.getWordRangeAtPosition(position, /PR-\d+/i);
        if (!range) {
          return null;
        }

        const hoveredText = document.getText(range);
        const prNumber = extractPrNumber(hoveredText);
        if (!prNumber) {
          return null;
        }

        const { apiBaseUrl, apiToken, repoOwner, repoName } = getConfig();

        try {
          const data = await fetchContext(
            apiBaseUrl,
            apiToken,
            repoOwner,
            repoName,
            prNumber
          );

          return new vscode.Hover(buildHoverMarkdown(data, prNumber), range);
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : String(err);
          return new vscode.Hover(
            new vscode.MarkdownString(`**GhostCommit**\n\nFailed to fetch context: ${msg}`),
            range
          );
        }
      },
    }
  );

  context.subscriptions.push(testCommand, hoverProvider);
}

export function deactivate() {}
import * as vscode from "vscode";

function getConfig() {
  const cfg = vscode.workspace.getConfiguration("ghostcommit");
  const apiBaseUrl = cfg.get<string>("apiBaseUrl", "http://localhost:8000");
  const apiToken = cfg.get<string>("apiToken", "");
  return { apiBaseUrl, apiToken };
}

async function pingHealth(apiBaseUrl: string): Promise<boolean> {
  const url = `${apiBaseUrl.replace(/\/$/, "")}/health`;
  const res = await fetch(url, { method: "GET" });
  return res.ok;
}

export function activate(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand("ghostcommit.test", async () => {
    const { apiBaseUrl, apiToken } = getConfig();

    try {
      const ok = await pingHealth(apiBaseUrl);

      if (!ok) {
        vscode.window.showErrorMessage(
          `GhostCommit Test failed: /health not OK at ${apiBaseUrl}. Check API container and URL setting.`
        );
        return;
      }

      const tokenStatus = apiToken?.trim() ? "set" : "not set";
      vscode.window.showInformationMessage(
        `GhostCommit Test OK ✅ API: ${apiBaseUrl} (token: ${tokenStatus})`
      );
    } catch (err: any) {
      vscode.window.showErrorMessage(
        `GhostCommit Test error: ${err?.message ?? String(err)}`
      );
    }
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}
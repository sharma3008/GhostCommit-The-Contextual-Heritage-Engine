"use strict";
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/extension.ts
var extension_exports = {};
__export(extension_exports, {
  activate: () => activate,
  deactivate: () => deactivate
});
module.exports = __toCommonJS(extension_exports);
var vscode = __toESM(require("vscode"));
function getConfig() {
  const cfg = vscode.workspace.getConfiguration("ghostcommit");
  const apiBaseUrl = cfg.get("apiBaseUrl", "http://localhost:8000");
  const apiToken = cfg.get("apiToken", "");
  return { apiBaseUrl, apiToken };
}
async function pingHealth(apiBaseUrl) {
  const url = `${apiBaseUrl.replace(/\/$/, "")}/health`;
  const res = await fetch(url, { method: "GET" });
  return res.ok;
}
function activate(context) {
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
        `GhostCommit Test OK \u2705 API: ${apiBaseUrl} (token: ${tokenStatus})`
      );
    } catch (err) {
      vscode.window.showErrorMessage(
        `GhostCommit Test error: ${err?.message ?? String(err)}`
      );
    }
  });
  context.subscriptions.push(disposable);
}
function deactivate() {
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  activate,
  deactivate
});
//# sourceMappingURL=extension.js.map

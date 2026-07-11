const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const htmlFiles = fs.readdirSync(root).filter((file) => file.endsWith(".html"));
const jsFiles = fs.readdirSync(path.join(root, "js")).filter((file) => file.endsWith(".js"));

const requiredScripts = ["js/data.js", "js/engine.js", "js/store.js", "js/ui.js"];

for (const file of htmlFiles) {
  const html = fs.readFileSync(path.join(root, file), "utf8");
  if (!html.includes('<meta name="viewport"')) throw new Error(`${file} missing viewport meta tag`);
  if (!html.includes('data-component="nav"')) throw new Error(`${file} missing shared nav component`);
  if (!html.includes('css/styles.css')) throw new Error(`${file} missing stylesheet`);
  if (file !== "index.html") {
    for (const script of requiredScripts) {
      if (!html.includes(script)) throw new Error(`${file} missing ${script}`);
    }
  }
}

for (const file of jsFiles) {
  const source = fs.readFileSync(path.join(root, "js", file), "utf8");
  if (source.includes("console.log(")) throw new Error(`${file} contains console.log`);
}

console.log(`Checked ${htmlFiles.length} HTML files and ${jsFiles.length} JavaScript files.`);

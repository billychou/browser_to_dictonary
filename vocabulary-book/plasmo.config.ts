import { defineConfig } from "plasmo"

export default defineConfig({
  name: "vocabulary-book",
  entry: {
    get: "./src/popup.tsx"
  },
  css: ["./src/style.css"],
  manifest: {
    permissions: ["storage"]
  }
})

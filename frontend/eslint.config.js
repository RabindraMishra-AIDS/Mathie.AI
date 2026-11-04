import tseslint from "typescript-eslint";

export default [
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    rules: {
      "@typescript-eslint/no-unused-vars": "error",
    },
  },
  {
    ignores: ["dist/**", "vite.config.d.ts", "vitest.config.d.ts"],
  },
];

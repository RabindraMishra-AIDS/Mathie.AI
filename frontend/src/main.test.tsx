import { beforeEach, describe, expect, it } from "vitest";
import { getPracticeChunk } from "./linearEquationChunks";

describe("app shell", () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="root"></div>';
  });

  it("provides a root mount point for the practice app", () => {
    expect(document.getElementById("root")).not.toBeNull();
  });

  it("keeps Practice Set 5 scoped to its registered PDF pages", () => {
    const chunk = getPracticeChunk(5);

    expect(chunk.pageStart).toBe(30);
    expect(chunk.pageEnd).toBe(36);
  });
});

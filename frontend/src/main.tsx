import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { getPracticeChunk, type PracticeChunk } from "./linearEquationChunks";

type Chapter = {
  name: string;
  sets: number[];
};

const chapters: Chapter[] = [
  { name: "Linear Equations in Two Variables", sets: [1, 2, 3, 4, 5] },
  { name: "Quadratic Equations", sets: [1, 2, 3, 4, 5, 6] },
  { name: "Arithmetic Progression", sets: [1, 2, 3, 4] },
  { name: "Financial Planning", sets: [1, 2, 3, 4] },
  { name: "Probability", sets: [1, 2, 3, 4] },
  { name: "Statistics", sets: [1, 2, 3, 5, 6] },
];

type View = "home" | "chapters" | "sets" | "practice" | "textbook" | "generator" | "concept";

type GeneratedPractice = {
  chapter: string;
  exercise: number;
  pages: string;
  topics: string[];
  problems: Array<{
    question: string;
    solution: string;
    explanation: string;
  }>;
  disclaimer: string;
  database_note: string;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function getApiError(response: Response, fallback: string): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (
      typeof body === "object" &&
      body !== null &&
      "detail" in body &&
      typeof body.detail === "string"
    ) {
      return body.detail;
    }
  } catch {
    return fallback;
  }
  return fallback;
}

function HomeIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24">
      <path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1V10Z" />
    </svg>
  );
}

function ArrowLeftIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24">
      <path d="m15 18-6-6 6-6M9 12h12" />
    </svg>
  );
}

function App() {
  const [view, setView] = useState<View>("home");
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  const [selectedChunk, setSelectedChunk] = useState<PracticeChunk | null>(null);
  const [generated, setGenerated] = useState<GeneratedPractice | null>(null);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const openChapters = () => setView("chapters");
  const openPracticeSets = (chapter: Chapter) => {
    setSelectedChapter(chapter);
    setSelectedChunk(null);
    setGenerated(null);
    setGenerationError(null);
    setView("sets");
  };
  const openSet = (setNumber: number) => {
    setSelectedChunk(getPracticeChunk(setNumber));
    setGenerated(null);
    setGenerationError(null);
    setView("practice");
  };
  const openGenerator = () => {
    setGenerated(null);
    setGenerationError(null);
    setView("generator");
  };
  const openTextbook = () => {
    setView("textbook");
  };
  const openConcept = () => {
    setGenerationError(null);
    setView("concept");
  };
  const generatePractice = async () => {
    if (!selectedChunk || !selectedChapter) return;
    setIsGenerating(true);
    setGenerationError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/practice/generate`, {
        body: JSON.stringify({
          chapter: selectedChapter.name,
          exercise: selectedChunk.setNumber,
          count: 5,
        }),
        headers: { "Content-Type": "application/json" },
        method: "POST",
      });
      if (!response.ok) {
        throw new Error(
          await getApiError(response, "The practice generator could not respond."),
        );
      }
      setGenerated((await response.json()) as GeneratedPractice);
    } catch (error) {
      setGenerationError(
        error instanceof Error
          ? error.message
          : "Unable to fetch generated problems right now.",
      );
    } finally {
      setIsGenerating(false);
    }
  };
  const goHome = () => {
    setSelectedChapter(null);
    setView("home");
  };

  return (
    <div className="app-shell">
      <header className="top-bar">
        <button className="brand" type="button" onClick={goHome} aria-label="Mathie.AI home">
          Mathie<span>.AI</span>
        </button>
        <p className="header-tagline">Train your mind. Defy the impossible.</p>
        {view !== "home" && (
          <button className="home-tab" type="button" onClick={goHome}>
            <HomeIcon />
            <span>Home</span>
          </button>
        )}
      </header>

      {view === "home" && (
        <main className="hero">
          <section className="hero-copy" aria-labelledby="page-title">
            <p className="eyebrow">Class 10 · Maharashtra State Board</p>
            <h1 id="page-title">Practice More!! Score more</h1>
            <p className="subject">Algebra Maths 1</p>
            <p className="intro">
              Enter the arena and sharpen your algebra skills with focused
              practice built for your board exams.
            </p>
            <button className="start-button" type="button" onClick={openChapters}>
              Start Practice <span aria-hidden="true">→</span>
            </button>
          </section>

          <section className="hero-art" aria-label="Mathie.AI practice illustration">
            <div className="image-frame">
              <img src="/image.png" alt="Mathie.AI learning illustration" />
            </div>
            <p className="art-caption">Your challenge awaits.</p>
          </section>
        </main>
      )}

      {view === "chapters" && (
        <main className="selection-page" aria-labelledby="chapters-title">
          <div className="selection-heading">
            <p className="eyebrow">Choose your challenge</p>
            <h1 id="chapters-title">Pick a chapter</h1>
            <p className="intro">Select a chapter to view its practice sets.</p>
          </div>
          <div className="option-grid chapter-grid">
            {chapters.map((chapter, index) => (
              <button
                className="option-card"
                key={chapter.name}
                type="button"
                onClick={() => openPracticeSets(chapter)}
              >
                <span className="option-number">{String(index + 1).padStart(2, "0")}</span>
                <span className="option-content">
                  <strong>{chapter.name}</strong>
                  <small>{chapter.sets.length} practice sets</small>
                </span>
                <span className="option-arrow" aria-hidden="true">→</span>
              </button>
            ))}
          </div>
        </main>
      )}

      {view === "sets" && selectedChapter && (
        <main className="selection-page" aria-labelledby="sets-title">
          <button className="back-button" type="button" onClick={openChapters}>
            <ArrowLeftIcon />
            Back to chapters
          </button>
          <div className="selection-heading">
            <p className="eyebrow">Chapter {chapters.indexOf(selectedChapter) + 1}</p>
            <h1 id="sets-title">{selectedChapter.name}</h1>
            <p className="intro">Choose a practice set and begin your session.</p>
          </div>
          <div className="option-grid practice-grid">
            {selectedChapter.sets.map((setNumber) => (
              <button
                className="option-card practice-card"
                key={setNumber}
                type="button"
                onClick={() => openSet(setNumber)}
              >
                <span className="option-number">0{setNumber}</span>
                <span className="option-content">
                  <strong>Practice Set {setNumber}</strong>
                  <small>Test your understanding</small>
                </span>
                <span className="option-arrow" aria-hidden="true">→</span>
              </button>
            ))}
          </div>
        </main>
      )}

      {view === "practice" && selectedChapter && selectedChunk && (
        <main className="selection-page" aria-labelledby="practice-title">
          <button className="back-button" type="button" onClick={() => setView("sets")}>
            <ArrowLeftIcon />
            Back to practice sets
          </button>
          <div className="selection-heading">
            <p className="eyebrow">Retrieved textbook context</p>
            <h1 id="practice-title">Practice Set {selectedChunk.setNumber}</h1>
            <p className="intro">
              {selectedChapter.name} · PDF pages {selectedChunk.pageStart}-{selectedChunk.pageEnd}.
              Only this page range is used for this practice set.
            </p>
          </div>
            <section className="practice-panel" aria-labelledby="practice-title">
              <div className="practice-panel-heading">
                <div>
                  <p className="eyebrow">Choose an activity</p>
                  <h2>Practice Set {selectedChunk.setNumber}</h2>
                </div>
                <span className="page-badge">
                  PDF pages {selectedChunk.pageStart}-{selectedChunk.pageEnd}
                </span>
              </div>
              <p className="context-note">
                Only this page range is used for this practice set.
              </p>
              <div className="topic-list">
                {selectedChunk.topics.map((topic) => <span key={topic}>{topic}</span>)}
              </div>
              <div className="action-row">
                <button className="action-button primary" type="button" onClick={openTextbook}>
                  Textbook practice problem
                </button>
                <button className="action-button" type="button" onClick={openGenerator}>
                  Generate new problems
                </button>
                <button className="action-button" type="button" onClick={openConcept}>
                  Concept and formulas
                </button>
              </div>
            </section>
        </main>
      )}

      {view === "textbook" && selectedChapter && selectedChunk && (
        <main className="selection-page" aria-labelledby="textbook-title">
          <button className="back-button" type="button" onClick={() => setView("practice")}>
            <ArrowLeftIcon />
            Back to practice set
          </button>
          <div className="selection-heading">
            <p className="eyebrow">Static textbook practice</p>
            <h1 id="textbook-title">Textbook practice problems</h1>
            <p className="intro">
              These examples come directly from the selected knowledge chunk. No
              generated content or LLM call is used.
            </p>
          </div>
          <section className="result-card standalone-result">
            <p className="context-note">
              {selectedChapter.name} · Practice Set {selectedChunk.setNumber} ·
              PDF pages {selectedChunk.pageStart}-{selectedChunk.pageEnd}
            </p>
            <ol>
              {selectedChunk.examples.map((example) => <li key={example}>{example}</li>)}
            </ol>
          </section>
        </main>
      )}

      {view === "generator" && selectedChapter && selectedChunk && (
        <main className="selection-page" aria-labelledby="generator-title">
          <button className="back-button" type="button" onClick={() => setView("practice")}>
            <ArrowLeftIcon />
            Back to practice set
          </button>
          <div className="selection-heading">
            <p className="eyebrow">AI practice studio</p>
            <h1 id="generator-title">Generate a fresh set</h1>
            <p className="intro">
              Problems are generated from Chapter {chapters.indexOf(selectedChapter) + 1},
              Practice Set {selectedChunk.setNumber}, and only its retrieved textbook pages.
              Each problem includes a worked solution and a short concept explanation.
            </p>
          </div>
          <section className="generator-panel" aria-label="Practice generation controls">
            <div className="generator-steps">
              <span><strong>01</strong> Filter metadata</span>
              <span><strong>02</strong> Retrieve pages {selectedChunk.pageStart}-{selectedChunk.pageEnd}</span>
              <span><strong>03</strong> Generate and verify</span>
            </div>
            <button className="action-button primary" type="button" onClick={generatePractice} disabled={isGenerating}>
              {isGenerating ? "Generating..." : "Generate 5 more practice problems"}
            </button>
            {generationError && (
              <div className="fallback-card" role="alert">
                <h2>{generationError}</h2>
                <p>No new problems were created. Try again shortly.</p>
              </div>
            )}
            {generated && (
              <div className="generated-results">
                <p className="context-note">Retrieved context: PDF pages {generated.pages}</p>
                <h2>Concept: {generated.topics.join(" · ")}</h2>
                {generated.problems.map((problem, index) => (
                  <article className="generated-problem" key={`${problem.question}-${index}`}>
                    <h3>Problem {index + 1}</h3>
                    <p><strong>{problem.question}</strong></p>
                    <p><span className="result-label">Solution:</span> {problem.solution}</p>
                    <p><span className="result-label">Why this works:</span> {problem.explanation}</p>
                  </article>
                ))}
                <p className="disclaimer">{generated.disclaimer}</p>
                <p className="database-note"><strong>How data is stored:</strong> {generated.database_note}</p>
              </div>
            )}
          </section>
        </main>
      )}

      {view === "concept" && selectedChapter && selectedChunk && (
        <main className="selection-page" aria-labelledby="concept-title">
          <button className="back-button" type="button" onClick={() => setView("practice")}>
            <ArrowLeftIcon />
            Back to practice set
          </button>
          <div className="selection-heading">
            <p className="eyebrow">Static textbook reference</p>
            <h1 id="concept-title">Concept and formulas</h1>
            <p className="intro">
              This reference is retrieved from the selected knowledge chunk.
              No LLM call is used.
            </p>
          </div>
          <section className="result-card standalone-result">
            <p className="context-note">
              {selectedChapter.name} · Practice Set {selectedChunk.setNumber} ·
              PDF pages {selectedChunk.pageStart}-{selectedChunk.pageEnd}
            </p>
            <div className="topic-list">
              {selectedChunk.topics.map((topic) => <span key={topic}>{topic}</span>)}
            </div>
            <p>{selectedChunk.context}</p>
          </section>
        </main>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

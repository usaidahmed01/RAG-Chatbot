/* =========================================
   FIFA 26 Premium UI Injection
   This creates a real landing hero above Chainlit chat.
========================================= */

(function () {
  const LOGO_PATH = "/public/fifa26-logo.png";

  const samplePrompts = [
    "Which countries are hosting the 2026 FIFA World Cup?",
    "Who won the 2022 FIFA World Cup?",
    "What is association football?",
    "How often is the FIFA World Cup held?",
    "What are some FIFA World Cup records?"
  ];

  function waitForApp(callback) {
    const interval = setInterval(() => {
      const bodyReady = document.body;
      const appReady =
        document.querySelector("main") ||
        document.querySelector("[data-testid]") ||
        document.querySelector("textarea");

      if (bodyReady && appReady) {
        clearInterval(interval);
        callback();
      }
    }, 300);
  }

  function createPitchParticles() {
    const existing = document.querySelector(".premium-pitch-particles");
    if (existing) return;

    const particles = document.createElement("div");
    particles.className = "premium-pitch-particles";

    for (let i = 0; i < 18; i += 1) {
      const dot = document.createElement("span");
      dot.style.setProperty("--x", `${Math.random() * 100}%`);
      dot.style.setProperty("--delay", `${Math.random() * 5}s`);
      dot.style.setProperty("--duration", `${4 + Math.random() * 6}s`);
      particles.appendChild(dot);
    }

    document.body.appendChild(particles);
  }

  function createHero() {
    if (document.querySelector("#fifa-premium-hero")) return;

    const hero = document.createElement("section");
    hero.id = "fifa-premium-hero";
    hero.innerHTML = `
      <div class="fifa-hero-shell">
        <div class="fifa-hero-left">
          <div class="fifa-live-badge">
            <span class="fifa-live-dot"></span>
            Football Knowledge Base · RAG System · World Cup 2026
          </div>

          <h1 class="fifa-hero-title">
            FIFA 26 Football<br>
            <span>RAG Chatbot</span>
          </h1>

          <p class="fifa-hero-subtitle">
            Ask grounded questions about football, FIFA World Cup history,
            records, hosts, qualification, and the 2026 FIFA World Cup.
          </p>

          <div class="fifa-tech-row">
            <span>LangChain</span>
            <span>ChromaDB</span>
            <span>HuggingFace</span>
            <span>Groq</span>
            <span>Chainlit</span>
          </div>

          <div class="fifa-hero-actions">
            <button class="fifa-primary-action" type="button" data-prompt="Which countries are hosting the 2026 FIFA World Cup?">
              Start with 2026 Hosts
            </button>
            <button class="fifa-secondary-action" type="button" data-prompt="Who won the 2022 FIFA World Cup?">
              Test 2022 Winner
            </button>
          </div>
        </div>

        <div class="fifa-hero-right">
          <div class="fifa-stadium-card">
            <div class="fifa-logo-glow"></div>
            <img src="${LOGO_PATH}" alt="FIFA World Cup 2026 Logo" class="fifa-hero-logo">
            <div class="fifa-score-card">
              <span>RAG</span>
              <strong>TOP-K</strong>
              <span>SOURCES</span>
            </div>
          </div>
        </div>
      </div>

      <div class="fifa-feature-grid">
        <div class="fifa-feature-card">
          <span class="fifa-feature-icon">📚</span>
          <h3>Open Dataset</h3>
          <p>Wikipedia football and World Cup articles with source metadata.</p>
        </div>

        <div class="fifa-feature-card">
          <span class="fifa-feature-icon">🧠</span>
          <h3>Strict RAG</h3>
          <p>Retrieval plus grounded generation to reduce hallucinations.</p>
        </div>

        <div class="fifa-feature-card">
          <span class="fifa-feature-icon">🏟️</span>
          <h3>Evidence First</h3>
          <p>Every answer displays retrieved chunks and verified source links.</p>
        </div>
      </div>

      <div class="fifa-prompt-panel">
        <div class="fifa-panel-title">
          <span>⚽</span>
          Try match-ready questions
        </div>
        <div class="fifa-prompt-grid"></div>
      </div>
    `;

    const main = document.querySelector("main");
    const root = main || document.body;
    root.prepend(hero);

    const promptGrid = hero.querySelector(".fifa-prompt-grid");

    samplePrompts.forEach((prompt) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "fifa-prompt-card";
      button.textContent = prompt;
      button.setAttribute("data-prompt", prompt);
      promptGrid.appendChild(button);
    });

    hero.addEventListener("click", function (event) {
      const target = event.target.closest("[data-prompt]");
      if (!target) return;

      const prompt = target.getAttribute("data-prompt");
      fillComposer(prompt);
    });
  }

  function fillComposer(text) {
    const textarea =
      document.querySelector("textarea") ||
      document.querySelector('[contenteditable="true"]');

    if (!textarea) return;

    textarea.focus();

    if ("value" in textarea) {
      textarea.value = text;
      textarea.dispatchEvent(new Event("input", { bubbles: true }));
      textarea.dispatchEvent(new Event("change", { bubbles: true }));
    } else {
      textarea.textContent = text;
      textarea.dispatchEvent(new InputEvent("input", { bubbles: true }));
    }

    const submitButton =
      document.querySelector("#chat-submit") ||
      document.querySelector('button[type="submit"]');

    if (submitButton) {
      setTimeout(() => {
        submitButton.disabled = false;
      }, 100);
    }
  }

  function enhanceComposerPlaceholder() {
    const interval = setInterval(() => {
      const textarea = document.querySelector("textarea");
      if (!textarea) return;

      textarea.setAttribute(
        "placeholder",
        "Ask about World Cup hosts, winners, records, teams..."
      );

      clearInterval(interval);
    }, 400);
  }

  function addScrollClass() {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 80) {
        document.body.classList.add("fifa-scrolled");
      } else {
        document.body.classList.remove("fifa-scrolled");
      }
    });
  }

  function observeAnswerAutoScroll() {
  let scrollTimer = null;
  let lastScrolledAnswer = "";

  function findLatestAnswerHeading() {
    const headings = Array.from(document.querySelectorAll("h1, h2, h3"));

    const answerHeadings = headings.filter((heading) => {
      const text = heading.textContent.trim().toLowerCase();
      return text.includes("answer") || text.includes("🎯");
    });

    if (!answerHeadings.length) return null;

    return answerHeadings[answerHeadings.length - 1];
  }

  function scrollToAnswer() {
    const answerHeading = findLatestAnswerHeading();

    if (!answerHeading) return;

    const marker = `${answerHeading.textContent}-${answerHeading.getBoundingClientRect().top}`;

    if (marker === lastScrolledAnswer) return;

    lastScrolledAnswer = marker;

    const answerContainer =
      answerHeading.closest('[data-testid*="message"]') ||
      answerHeading.closest("article") ||
      answerHeading.closest("[class*='message']") ||
      answerHeading;

    setTimeout(() => {
      answerContainer.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }, 120);

    setTimeout(() => {
      answerContainer.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }, 650);
  }

  const observer = new MutationObserver(() => {
    clearTimeout(scrollTimer);

    scrollTimer = setTimeout(() => {
      scrollToAnswer();
    }, 350);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true
  });

function hideAttachmentButton() {
  function removeAttachmentButtons() {
    const buttons = Array.from(document.querySelectorAll("button"));

    buttons.forEach((button) => {
      const ariaLabel = (button.getAttribute("aria-label") || "").toLowerCase();
      const title = (button.getAttribute("title") || "").toLowerCase();
      const text = (button.textContent || "").toLowerCase();

      const isAttachmentButton =
        ariaLabel.includes("attach") ||
        ariaLabel.includes("upload") ||
        ariaLabel.includes("file") ||
        ariaLabel.includes("pin") ||
        title.includes("attach") ||
        title.includes("upload") ||
        title.includes("file") ||
        title.includes("pin") ||
        text.includes("attach") ||
        text.includes("upload");

      if (isAttachmentButton) {
        button.style.display = "none";
        button.setAttribute("aria-hidden", "true");
        button.setAttribute("tabindex", "-1");
      }
    });
  }

  removeAttachmentButtons();

  const observer = new MutationObserver(() => {
    removeAttachmentButtons();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

}

  waitForApp(() => {
    createPitchParticles();
    createHero();
    enhanceComposerPlaceholder();
    addScrollClass();
    observeAnswerAutoScroll();
    hideAttachmentButton();
  });
})();
/**
 * Central article index.
 * Used by blog.html and search.html for client-side filtering.
 * Keeping this in one file means the article list only has to be
 * maintained in one place.
 */
const ARTICLES = [
  {
    title: "Getting Started with Python: A Student's Roadmap",
    slug: "articles/python-roadmap.html",
    excerpt: "A practical, no-fluff path from installing Python to writing your first useful scripts — what to learn first and what to skip.",
    category: "Programming",
    tags: ["python", "beginners"],
    date: "2026-01-12",
    readTime: "7 min read"
  },
  {
    title: "Understanding Variables and Data Types in Programming",
    slug: "articles/variables-data-types.html",
    excerpt: "Why variables and types trip up so many beginners, explained with plain analogies and short examples in Python and JavaScript.",
    category: "Programming",
    tags: ["fundamentals", "beginners"],
    date: "2026-01-19",
    readTime: "6 min read"
  },
  {
    title: "What Is Machine Learning? A Beginner's Guide for Students",
    slug: "articles/what-is-machine-learning.html",
    excerpt: "Machine learning without the hype: how it actually differs from normal programming, and the three learning styles you'll hear about.",
    category: "AI",
    tags: ["ai", "machine-learning"],
    date: "2026-02-02",
    readTime: "8 min read"
  },
  {
    title: "Git and GitHub Basics Every Student Should Know",
    slug: "articles/git-github-basics.html",
    excerpt: "The handful of Git commands that cover 95% of real student work, plus a mental model for what's actually happening under the hood.",
    category: "Tools",
    tags: ["git", "tools"],
    date: "2026-02-14",
    readTime: "7 min read"
  },
  {
    title: "How Neural Networks Actually Work (Explained Simply)",
    slug: "articles/neural-networks-explained.html",
    excerpt: "Forget the brain metaphors for a minute — here's what a neural network is actually computing, step by step, with a tiny worked example.",
    category: "AI",
    tags: ["ai", "neural-networks"],
    date: "2026-03-01",
    readTime: "9 min read"
  },
  {
    title: "10 VS Code Extensions That Will Boost Your Coding Productivity",
    slug: "articles/vscode-extensions.html",
    excerpt: "A curated, student-tested list of extensions that actually save time — not just the ones every listicle repeats.",
    category: "Tools",
    tags: ["vscode", "productivity"],
    date: "2026-03-10",
    readTime: "6 min read"
  },
  {
    title: "Data Structures Every CS Student Must Master",
    slug: "articles/data-structures-guide.html",
    excerpt: "Arrays, linked lists, stacks, queues, trees, and hash maps — what each one is actually good for, not just how to implement it.",
    category: "Computer Science",
    tags: ["data-structures", "cs-fundamentals"],
    date: "2026-03-22",
    readTime: "9 min read"
  },
  {
    title: "Building Your First REST API with Python and Flask",
    slug: "articles/flask-rest-api.html",
    excerpt: "A hands-on walkthrough of building a small, real API in Flask — routes, JSON responses, and testing it with your browser.",
    category: "Programming",
    tags: ["python", "flask", "web-dev"],
    date: "2026-04-05",
    readTime: "10 min read"
  },
  {
    title: "How to Read and Debug Error Messages Like a Pro",
    slug: "articles/debug-error-messages.html",
    excerpt: "Stack traces look scary until you know where to look. A calm, repeatable process for turning an error into a fix.",
    category: "Programming",
    tags: ["debugging", "beginners"],
    date: "2026-04-18",
    readTime: "7 min read"
  },
  {
    title: "AI Ethics 101: What Every Programmer Should Understand",
    slug: "articles/ai-ethics-101.html",
    excerpt: "Bias, consent, and accountability aren't someone else's problem — a grounded introduction for students who will build these systems.",
    category: "AI",
    tags: ["ai", "ethics"],
    date: "2026-05-02",
    readTime: "8 min read"
  }
];

if (typeof module !== "undefined") { module.exports = ARTICLES; }

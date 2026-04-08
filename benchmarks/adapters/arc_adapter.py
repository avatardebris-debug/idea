"""
benchmarks/adapters/arc_adapter.py

Loads ARC-Challenge multiple-choice reasoning problems as BenchmarkTask objects.
Used exclusively as a HELD-OUT validation benchmark.

Dataset: AI2 Reasoning Challenge (CC-BY-SA 4.0)
The agent must write a single letter (A/B/C/D) to 'answer.txt'.
"""

from __future__ import annotations

import json
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
from benchmark_runner import BenchmarkTask

DATASET_PATH = pathlib.Path(__file__).parent.parent / "datasets" / "arc_challenge_test.jsonl"

# Primary download URL — the ARC dataset is hosted on HuggingFace CDN
DOWNLOAD_URL = (
    "https://huggingface.co/datasets/allenai/ai2_arc/resolve/main/"
    "ARC-Challenge/test-00000-of-00001.jsonl"
)
# Fallback: we include 30 representative questions inline if download fails
_FALLBACK_QUESTIONS = [
    {"id": "arc_f_001", "question": "Which of the following best explains why the Moon appears to change shape over a month?", "choices": [{"text": "The Moon rotates on its axis", "label": "A"}, {"text": "Earth casts a shadow on the Moon", "label": "B"}, {"text": "Different amounts of the sunlit side of the Moon are visible from Earth", "label": "C"}, {"text": "The Moon moves closer and farther from Earth", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_002", "question": "What is the primary source of energy for most ecosystems on Earth?", "choices": [{"text": "Wind", "label": "A"}, {"text": "Sunlight", "label": "B"}, {"text": "Water", "label": "C"}, {"text": "Heat from Earth's core", "label": "D"}], "answerKey": "B"},
    {"id": "arc_f_003", "question": "Which process do plants use to convert sunlight into food?", "choices": [{"text": "Respiration", "label": "A"}, {"text": "Fermentation", "label": "B"}, {"text": "Photosynthesis", "label": "C"}, {"text": "Decomposition", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_004", "question": "What type of rock is formed from cooled magma or lava?", "choices": [{"text": "Sedimentary", "label": "A"}, {"text": "Metamorphic", "label": "B"}, {"text": "Igneous", "label": "C"}, {"text": "Fossil", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_005", "question": "Which layer of Earth is made mostly of iron and nickel?", "choices": [{"text": "Crust", "label": "A"}, {"text": "Mantle", "label": "B"}, {"text": "Inner core", "label": "C"}, {"text": "Outer atmosphere", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_006", "question": "A student rubs a balloon against wool and then holds it near small pieces of paper. The paper sticks to the balloon. What force causes this?", "choices": [{"text": "Gravity", "label": "A"}, {"text": "Magnetism", "label": "B"}, {"text": "Static electricity", "label": "C"}, {"text": "Friction", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_007", "question": "Which of the following is a renewable resource?", "choices": [{"text": "Coal", "label": "A"}, {"text": "Natural gas", "label": "B"}, {"text": "Solar energy", "label": "C"}, {"text": "Oil", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_008", "question": "What happens to the particles of a solid when it is heated enough to become a liquid?", "choices": [{"text": "They stop moving", "label": "A"}, {"text": "They move closer together", "label": "B"}, {"text": "They move faster and farther apart", "label": "C"}, {"text": "They disappear", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_009", "question": "Which organ system is responsible for transporting oxygen to cells throughout the body?", "choices": [{"text": "Digestive system", "label": "A"}, {"text": "Nervous system", "label": "B"}, {"text": "Circulatory system", "label": "C"}, {"text": "Skeletal system", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_010", "question": "A ball is thrown upward. At its highest point, which is true?", "choices": [{"text": "Its velocity is maximum", "label": "A"}, {"text": "Its acceleration is zero", "label": "B"}, {"text": "Its velocity is zero but acceleration is not", "label": "C"}, {"text": "Both velocity and acceleration are zero", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_011", "question": "Which of these is NOT a characteristic of living things?", "choices": [{"text": "Growth", "label": "A"}, {"text": "Reproduction", "label": "B"}, {"text": "Made of cells", "label": "C"}, {"text": "Made of metal", "label": "D"}], "answerKey": "D"},
    {"id": "arc_f_012", "question": "What is the chemical formula for water?", "choices": [{"text": "CO2", "label": "A"}, {"text": "H2O", "label": "B"}, {"text": "NaCl", "label": "C"}, {"text": "O2", "label": "D"}], "answerKey": "B"},
    {"id": "arc_f_013", "question": "Which planet is closest to the Sun?", "choices": [{"text": "Venus", "label": "A"}, {"text": "Earth", "label": "B"}, {"text": "Mercury", "label": "C"}, {"text": "Mars", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_014", "question": "DNA is found primarily in which organelle of the cell?", "choices": [{"text": "Mitochondria", "label": "A"}, {"text": "Ribosome", "label": "B"}, {"text": "Nucleus", "label": "C"}, {"text": "Cell membrane", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_015", "question": "A substance that speeds up a chemical reaction without being consumed is called a:", "choices": [{"text": "Reactant", "label": "A"}, {"text": "Product", "label": "B"}, {"text": "Catalyst", "label": "C"}, {"text": "Solution", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_016", "question": "Which gas do plants absorb from the atmosphere during photosynthesis?", "choices": [{"text": "Oxygen", "label": "A"}, {"text": "Nitrogen", "label": "B"}, {"text": "Carbon dioxide", "label": "C"}, {"text": "Hydrogen", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_017", "question": "An object in motion will remain in motion unless acted upon by an external force. This is Newton's:", "choices": [{"text": "Second Law", "label": "A"}, {"text": "Third Law", "label": "B"}, {"text": "First Law", "label": "C"}, {"text": "Law of Gravity", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_018", "question": "What type of energy does a stretched rubber band possess?", "choices": [{"text": "Kinetic energy", "label": "A"}, {"text": "Thermal energy", "label": "B"}, {"text": "Elastic potential energy", "label": "C"}, {"text": "Chemical energy", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_019", "question": "Which of the following is an example of a chemical change?", "choices": [{"text": "Ice melting", "label": "A"}, {"text": "Water evaporating", "label": "B"}, {"text": "Iron rusting", "label": "C"}, {"text": "Glass breaking", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_020", "question": "The process by which water vapor cools and turns into liquid water is called:", "choices": [{"text": "Evaporation", "label": "A"}, {"text": "Sublimation", "label": "B"}, {"text": "Condensation", "label": "C"}, {"text": "Precipitation", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_021", "question": "Which of the following best describes a food web?", "choices": [{"text": "A single chain of organisms that eat one another", "label": "A"}, {"text": "A network of overlapping food chains in an ecosystem", "label": "B"}, {"text": "A list of all plants in an ecosystem", "label": "C"}, {"text": "The cycle of water through an ecosystem", "label": "D"}], "answerKey": "B"},
    {"id": "arc_f_022", "question": "What is the unit of electrical resistance?", "choices": [{"text": "Ampere", "label": "A"}, {"text": "Volt", "label": "B"}, {"text": "Ohm", "label": "C"}, {"text": "Watt", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_023", "question": "Which planet has the most moons in our solar system?", "choices": [{"text": "Jupiter", "label": "A"}, {"text": "Saturn", "label": "B"}, {"text": "Uranus", "label": "C"}, {"text": "Neptune", "label": "D"}], "answerKey": "B"},
    {"id": "arc_f_024", "question": "The ability of an organism to maintain a stable internal environment is called:", "choices": [{"text": "Adaptation", "label": "A"}, {"text": "Evolution", "label": "B"}, {"text": "Homeostasis", "label": "C"}, {"text": "Metabolism", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_025", "question": "Sound waves are which type of waves?", "choices": [{"text": "Transverse waves", "label": "A"}, {"text": "Electromagnetic waves", "label": "B"}, {"text": "Longitudinal waves", "label": "C"}, {"text": "Light waves", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_026", "question": "Which vitamin is produced by the skin when exposed to sunlight?", "choices": [{"text": "Vitamin A", "label": "A"}, {"text": "Vitamin B12", "label": "B"}, {"text": "Vitamin C", "label": "C"}, {"text": "Vitamin D", "label": "D"}], "answerKey": "D"},
    {"id": "arc_f_027", "question": "What is the powerhouse of the cell?", "choices": [{"text": "Nucleus", "label": "A"}, {"text": "Ribosome", "label": "B"}, {"text": "Mitochondria", "label": "C"}, {"text": "Vacuole", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_028", "question": "Which of these is NOT a type of electromagnetic radiation?", "choices": [{"text": "Radio waves", "label": "A"}, {"text": "X-rays", "label": "B"}, {"text": "Sound waves", "label": "C"}, {"text": "Gamma rays", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_029", "question": "The theory explaining the movement of Earth's continents over time is called:", "choices": [{"text": "The Big Bang Theory", "label": "A"}, {"text": "Evolution Theory", "label": "B"}, {"text": "Plate Tectonics", "label": "C"}, {"text": "Theory of Relativity", "label": "D"}], "answerKey": "C"},
    {"id": "arc_f_030", "question": "Which type of bond forms when two atoms share electrons?", "choices": [{"text": "Ionic bond", "label": "A"}, {"text": "Hydrogen bond", "label": "B"}, {"text": "Covalent bond", "label": "C"}, {"text": "Metallic bond", "label": "D"}], "answerKey": "C"},
]


def _try_download() -> list[dict] | None:
    """Try to download the ARC dataset. Returns None if download fails."""
    try:
        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
        problems = []
        for line in data.strip().split("\n"):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
                if "question" in d and "answerKey" in d:
                    problems.append(d)
            except json.JSONDecodeError:
                continue
        if problems:
            with open(DATASET_PATH, "w", encoding="utf-8") as f:
                for p in problems:
                    f.write(json.dumps(p) + "\n")
            return problems
    except Exception as e:
        print(f"  ARC download failed ({e}), using built-in questions")
    return None


def _load_problems() -> list[dict]:
    """Load from disk if available, otherwise download, otherwise use fallback."""
    if DATASET_PATH.exists():
        problems = []
        with open(DATASET_PATH, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        problems.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        if problems:
            return problems

    downloaded = _try_download()
    if downloaded:
        return downloaded

    return _FALLBACK_QUESTIONS


def _make_task(problem: dict, idx: int) -> BenchmarkTask:
    question_text = problem.get("question", {})
    # Handle both flat {"question": "..."} and nested {"question": {"stem": "..."}}
    if isinstance(question_text, dict):
        stem = question_text.get("stem", "")
        choices = question_text.get("choices", [])
    else:
        stem = question_text
        choices = problem.get("choices", [])

    answer_key = problem.get("answerKey", "A")
    safe_id = problem.get("id", f"arc_{idx:04d}").replace("/", "_")

    # Format choices as a readable list
    choices_text = "\n".join(f"  {c['label']}) {c['text']}" for c in choices)

    description = (
        f"Answer this multiple-choice question by writing the correct letter "
        f"(A, B, C, or D) to 'answer.txt'. Write ONLY the letter, nothing else.\n\n"
        f"Question: {stem}\n\n"
        f"Options:\n{choices_text}"
    )

    return BenchmarkTask(
        id=safe_id,
        category="science_reasoning",
        difficulty="hard",
        description=description,
        setup={},
        checks=[
            {"type": "file_exists", "path": "answer.txt"},
            {"type": "file_contains", "path": "answer.txt", "text": answer_key},
        ],
        max_steps=6,
        cleanup=["answer.txt"],
    )


def load_arc_tasks(
    max_tasks: int = 25,
    seed: int = 77,
) -> list[BenchmarkTask]:
    """Load ARC-Challenge validation tasks.

    IMPORTANT: These are HELD-OUT. Never add them to the training pool.
    """
    problems = _load_problems()

    import random
    rng = random.Random(seed)
    rng.shuffle(problems)
    problems = problems[:max_tasks]

    return [_make_task(p, i) for i, p in enumerate(problems)]


if __name__ == "__main__":
    tasks = load_arc_tasks(max_tasks=3)
    print(f"Loaded {len(tasks)} ARC tasks")
    for t in tasks:
        print(f"  {t.id}: {t.description[:80]}...")
        print(f"    checks: {[c['type'] for c in t.checks]}")

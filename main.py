"""Point d'entree : lancez `python main.py` pour discuter avec votre agent."""
from agent import run_agent

if __name__ == "__main__":
    print("Agent pret. Tapez votre question (ou 'quit' pour sortir).")
    while True:
        question = input("> ")
        if question.lower() in {"quit", "exit"}:
            break
        print(run_agent(question))

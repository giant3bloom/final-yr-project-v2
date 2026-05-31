"""CLI entry: python -m NexAI.optimizer.main"""
from NexAI.runtime.bootstrap import bootstrap

bootstrap()

from NexAI.optimizer.runner import main


if __name__ == "__main__":
    main()

import random

from pydoover.docker import Application, run_app


class SampleSimulator(Application):
    async def setup(self):
        pass

    async def main_loop(self):
        await self.set_tag("random_value", random.randint(1, 100))


def main():
    """Run the sample simulator application."""
    run_app(SampleSimulator())


if __name__ == "__main__":
    main()

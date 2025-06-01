from abc import ABC, abstractmethod
from bulletchess import Board


class BaseEngine(ABC):
    def __init__(self, player: str):
        self.max_player = player

    @abstractmethod
    def select_move(self, board: Board):
        """Selects the next move to make."""
        pass


    def get_html_board(self, board: Board, filename: str = "board"):
        move_number = board.fullmove_number
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>BulletChess Viewer</title>
        </head>
        <body>
            <div id="move-number" style="font-family: sans-serif; font-size: 20px; margin: 10px;">
                Move: {move_number}
            </div>
            {board._repr_html_()}

            <script>
                let lastModified = null;

                async function checkForUpdate() {{
                    try {{
                        const response = await fetch("{filename}.html", {{ method: "HEAD" }});
                        const newModified = response.headers.get("Last-Modified");

                        if (lastModified && newModified !== lastModified) {{
                            location.reload();
                        }}

                        lastModified = newModified;
                    }} catch (err) {{
                        console.error("Error checking for updates", err);
                    }}
                }}

                setInterval(checkForUpdate, 500);  // Check every second
            </script>
        </body>
        </html>
        """
        with open(f"{filename}.html", "w") as file:
            file.write(html)

import json
import os
from dotenv import load_dotenv

# this is a gross abuse of the as keyword
# that would get you laughed out of a FAANG company;
# why is it bad?
# when you reference "calculate_tool",
# it is much harder to understand where this function comes from;
# this will cause both human and AIs extending your code
# to get confused and bug out
from tools.calculate import calculate as calculate_tool
from tools.cat import cat as cat_tool
from tools.grep import grep as grep_tool
from tools.ls import ls as ls_tool
from tools.compact import compact as compact_tool

from groq import Groq
# you shouldn't be trying to check if groq is installed;
# this is an anti-pattern; just let python crash


load_dotenv()


class Chat:
    """Chat interface that exposes tools and optional Groq LLM support.

    The Chat class provides methods for calculation, file listing, file reading, and pattern search.
    It can also run a remote conversation if a Groq client is configured.
    """

    def __init__(self, client=None, api_key=None):
        """Initialize the Chat object with optional Groq client support.

        >>> chat = Chat()
        
        # neither of these test cases actually tested anything meaningful
        """
        self.model = "llama-3.1-8b-instant"
        self.messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant with access to tools. Be concise and direct in your responses.""",
                # the details about when to use which tools should be included directly in the tool description;
                # this makes adding new tools (or modifying existing tools) easier
                # because you only have to modify things in one place
            }
        ]

        if client is not None:
            self.client = client
        elif api_key is not None:
            self.client = Groq(api_key=api_key)
        else:
            env_key = os.getenv("GROQ_API_KEY")
            self.client = Groq(api_key=env_key) if env_key and Groq is not None else None

    def send_message(self, message, temperature=0.0):
        """Append a user message and optionally send it to the configured LLM.

        >>> from unittest.mock import Mock
        >>> mock_client = Mock()
        >>> mock_completion = Mock()
        >>> mock_message = Mock()
        >>> mock_message.content = 'Hello back!'
        >>> mock_choice = Mock()
        >>> mock_choice.message = mock_message
        >>> mock_completion.choices = [mock_choice]
        >>> mock_client.chat.completions.create.return_value = mock_completion
        >>> chat = Chat(client=mock_client)
        >>> chat.send_message('hello', temperature=0.0)
        'Hello back!'
        >>> import os
        >>> os.environ["GROQ_API_KEY"] = ""
        >>> chat = Chat(client=None)
        >>> chat.send_message('hello')
        'No Groq client configured.'

        # these are some pretty ugly tests here that don't actually demonstrate
        # that the llm functionality works
        """
        self.messages.append({"role": "user", "content": message})

        if self.client is None:
            return "No Groq client configured."

        completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            temperature=temperature,
        )
        return completion.choices[0].message.content

    # you shouldn't be defining new methods in this class for each tool you use;
    # again, this makes defining new tools much harder in the future
    # and doesn't give you any benefit;
    # I modified the place where you invoke these functions to just use the tool directly

    def run_conversation(self, user_prompt):
        """Run a conversation through the configured Groq client.
        Doctests for this method use mocking to simulate Groq client responses, without the need for an actual API key.

        # again, super gross tests that don't actually test your functionality
        >>> from unittest.mock import Mock 
        >>> mock_client = Mock()
        >>> mock_client = Mock()
        >>> mock_response = Mock()
        >>> mock_message = Mock()
        >>> mock_message.content = 'I can help with that.'
        >>> mock_message.tool_calls = None
        >>> mock_choice = Mock()
        >>> mock_choice.message = mock_message
        >>> mock_response.choices = [mock_choice]
        >>> mock_client.chat.completions.create.return_value = mock_response
        >>> chat = Chat(client=mock_client)
        >>> chat.run_conversation('hello')
        'I can help with that.'
        >>> # Test tool calling path
        >>> import json
        >>> mock_tool_call = Mock()
        >>> mock_tool_call.id = 'call_123'
        >>> mock_tool_call.function.name = 'calculate'
        >>> mock_tool_call.function.arguments = '{"expression": "2+2"}'
        >>> mock_message_with_tools = Mock()
        >>> mock_message_with_tools.content = ''
        >>> mock_message_with_tools.tool_calls = [mock_tool_call]
        >>> mock_response_with_tools = Mock()
        >>> mock_response_with_tools.choices = [Mock()]
        >>> mock_response_with_tools.choices[0].message = mock_message_with_tools
        >>> mock_second_response = Mock()
        >>> mock_second_message = Mock()
        >>> mock_second_message.content = 'The result is 4'
        >>> mock_second_choice = Mock()
        >>> mock_second_choice.message = mock_second_message
        >>> mock_second_response.choices = [mock_second_choice]
        >>> mock_client.chat.completions.create.side_effect = [mock_response_with_tools, mock_second_response]
        >>> chat.run_conversation('calculate 2+2')
        'The result is 4'
        """
        if self.client is None:
            return "Groq client is required to run conversations."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "You can use tools to calculate math expressions and list files."
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

        # these tool schemas should not be here;
        # they should be in the same file as the tool python code;
        # again: keep everything about a tool in just one place
        # so that it is easy to add/modify tools in the future
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Evaluate a mathematical expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The mathematical expression to evaluate",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "ls",
                    "description": "List all files and directories in a directory. Use this when the user asks what files are in a directory or to list contents. Do NOT use this to read file contents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Optional directory path to list files from",
                            }
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "grep",
                    "description": "Search for lines matching a regex pattern in files matching a glob pattern",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "regex": {
                                "type": "string",
                                "description": "The regex pattern to search for",
                            },
                            "filepath": {
                                "type": "string",
                                "description": "The file path or glob pattern to search in",
                            },
                        },
                        "required": ["regex", "filepath"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "cat",
                    "description": "Read and display the complete contents of a single file. Use this when the user asks to read, view, show, or display a file's content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "The name of the file to read",
                            }
                        },
                        "required": ["filename"],
                    },
                },
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature, # we don't want magic values; this should be a parameter to the function;
            # also, temp of 0 will result in worse realworld performance
            # and should only be used in test cases;
            # this is one possible reason (among many) for your ls tool not getting invoked
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {
                "calculate": calculate_tool,
                "ls": ls_tool,
                "grep": grep_tool,
                "cat": cat_tool,
            }

            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                function_args = json.loads(tool_call.function.arguments)

                if function_to_call is None:
                    function_response = json.dumps(
                        {"error": f"Unknown function: {function_name}"}
                    )
                else:
                    function_response = function_to_call(**function_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return second_response.choices[0].message.content

        return response_message.content

    # evrything in your compact method should be in the tools/compact.py folder;

def main():
    """Start the chat command line interface.

    >>> import builtins
    >>> import io
    >>> import contextlib
    >>> import os
    >>> import sys

    >>> original_input = builtins.input
    >>> original_getenv = os.getenv
    >>> original_chat_class = Chat

    >>> class FakeChat:
    ...     def calculate(self, expression):
    ...         return f"CALC:{expression}"
    ...     def ls(self, path=None):
    ...         return f"LS:{path}"
    ...     def grep(self, regex, filepath):
    ...         return f"GREP:{regex}:{filepath}"
    ...     def cat(self, filename):
    ...         return f"CAT:{filename}"
    ...     def run_conversation(self, user_prompt):
    ...         return f"CHAT:{user_prompt}"
    ...     def compact(self):
    ...         return "Conversation compacted."

    >>> builtins.input = lambda prompt: next(inputs)
    >>> os.getenv = lambda key: None
    >>> sys.modules[__name__].Chat = FakeChat

    >>> inputs = iter([
    ...     "/",
    ...     "/calculate",
    ...     "/calculate 2+2",
    ...     "/calculate 4 + 5",
    ...     "/ls",
    ...     "/ls dir",
    ...     "/grep",
    ...     "/grep a file.txt",
    ...     "/cat",
    ...     "/cat file.txt",
    ...     "/compact",
    ...     "/unknown cmd",
    ...     "hello",
    ... ])

    >>> output = io.StringIO()
    >>> with contextlib.redirect_stdout(output):
    ...     try:
    ...         main()
    ...     except StopIteration:
    ...         print()

    # this test does actually test stuff,
    # but it's unreadable to a human because the inputs are not next to the outputs
    >>> print(output.getvalue(), end="")
    Groq client is not configured. Only local tools are available.
    Invalid command
    Usage: /calculate <expression>
    CALC:2+2
    CALC:4 + 5
    LS:None
    LS:dir
    Usage: /grep <regex> <filepath>
    GREP:a:file.txt
    Usage: /cat <filename>
    CAT:file.txt
    Conversation compacted.
    Unknown command: unknown
    CHAT:hello
    <BLANKLINE>

    >>> builtins.input = original_input
    >>> os.getenv = original_getenv
    >>> sys.modules[__name__].Chat = original_chat_class
    """
    if os.getenv("GROQ_API_KEY") is None:
        print("Groq client is not configured. Only local tools are available.")

    chat = Chat()

    try:
        while True:
            user_input = input("chat>> ")
            if user_input.startswith("/"):
                parts = user_input[1:].split(maxsplit=1)
                if not parts:
                    print("Invalid command")
                    continue
                command, *args = parts
                if command == "calculate":
                    if len(args) != 1:
                        print("Usage: /calculate <expression>")
                        continue
                    print(chat.calculate(args[0]))
                elif command == "ls":
                    print(chat.ls(args[0] if args else None))
                elif command == "grep":
                    if len(args) != 1:
                        print("Usage: /grep <regex> <filepath>")
                        continue
                    grep_parts = args[0].split(maxsplit=1)
                    if len(grep_parts) != 2:
                        print("Usage: /grep <regex> <filepath>")
                        continue
                    print(chat.grep(grep_parts[0], grep_parts[1]))
                elif command == "cat":
                    if len(args) != 1:
                        print("Usage: /cat <filename>")
                        continue
                    print(chat.cat(args[0]))
                elif command == "compact":
                    print(chat.compact())
                else:
                    print(f"Unknown command: {command}")
            else:
                print(chat.run_conversation(user_input))
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()

    



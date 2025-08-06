class StatusCodeError(Exception):
    """Custom exception for handling HTTP status code errors."""

    def __init__(self, status_code, message=""):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message

class StatusResponseException:
    def __init__(self) -> None:
        self.response_code_dict = {
            200: (
                "200 OK\n"
                "Request successful."),
            
            400: (
                "400 Bad Request\n"
                "- Syntax error in the request.\n"
                "- Possible Issues:\n"
                "  • Wrong parameter format (e.g., string instead of int)\n"
                "  • Invalid parameter values (e.g., too large a time range)\n"
                "  • Required parameter missing."
            ),
            
            401: (
                "401 Unauthorized\n"
                "- Missing authentication credentials (e.g., API key).\n"
                "- Fix:\n"
                "  • Ensure API key is included in the request."
                "  • Also ensure that the API key is not outdated."
            ),
            
            403: (
                "403 Forbidden\n"
                "- Server understood request but refuses to authorize.\n"
                "- Possible Issues:\n"
                "  • Invalid or blacklisted API key\n"
                "  • Incorrect or unsupported request path."
            ),
            
            404: (
                "404 Not Found\n"
                "- No matching resource found.\n"
                "- Possible Issues:\n"
                "  • Invalid ID or name\n"
                "  • Parameters return no results."
            ),
            
            405: (
                "405 Method Not Allowed\n"
                "- HTTP method not supported for this endpoint."),
            
            415: (
                "415 Unsupported Media Type\n"
                "- Request body format not supported.\n"
                "- Fix:\n"
                "  • Set the correct Content-Type header (e.g., application/json)."
            ),
            
            429: (
                "429 Rate Limit Exceeded\n"
                "- Too many requests sent in a given time frame.\n"
                "- Fix:\n"
                "  • Respect the Retry-After header.\n"
                "  • Avoid unregulated API calls."
            ),
            
            500: (
                "500 Internal Server Error\n"
                "- Unexpected server error occurred.\n"
                r"- This is likely a problem on the API provider’s side."
            ),
            
            502: (
                "502 Bad Gateway\n"
                "- Invalid response received from upstream server."),
            
            503: (
                "503 Service Unavailable\n"
                "- Server temporarily unable to handle the request.\n"
                "- Try again later."
            ),
            
            504: (
                "504 Gateway Timeout\n"
                "- The server did not receive a timely response from upstream.")
        }
    def get_response_codes(self) -> list:

        return list(self.response_code_dict.keys())
        
    def raise_error(self, status_code: int) -> None:
        """
        Handles different HTTP status codes and raises exceptions if the status code is not 200.

        Args:
            status_code (int): The HTTP status code from the API response.

        Raises:
            StatusCodeError: If the status code is not 200, raises a custom exception with a message.

        Returns:
            bool: True if the status code is 200, otherwise raises an exception.
        """


        if status_code != 200:
            raise StatusCodeError(
                status_code, self.response_code_dict[status_code])
        

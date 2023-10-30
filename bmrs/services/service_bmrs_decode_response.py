from bmrs.services import logger


class ServiceBmrsDecodeResponse:
    
    @staticmethod
    def decode(content: bytes, encoding: str = "utf-8") -> str:
        """
        Decodes the given content using the specified encoding.

        Args:
            content: The byte content to decode.
            encoding: The encoding to use. Default is 'utf-8'.

        Returns:
            The decoded string.
        """
        
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            logger.error(f"Failed to decode content using '{encoding}' encoding.")
            return None

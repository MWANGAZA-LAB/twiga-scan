from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PluginConfig(BaseModel):
    """Base configuration for plugins"""

    name: str
    version: str
    description: str
    author: str
    enabled: bool = True
    settings: Dict[str, Any] = {}


class ScanResult(BaseModel):
    """Standardized scan result format"""

    content_type: str
    parsed_data: Dict[str, Any]
    raw_content: str
    validation: Dict[str, bool]
    metadata: Dict[str, Any] = {}


class BaseParser(ABC):
    """Base class for all parsers"""

    def __init__(self, config: PluginConfig):
        self.config = config

    @abstractmethod
    def can_parse(self, content: str) -> bool:
        """Check if this parser can handle the given content"""
        pass

    @abstractmethod
    def parse(self, content: str) -> ScanResult:
        """Parse the content and return standardized result"""
        pass

    @abstractmethod
    def validate(self, parsed_data: Dict[str, Any]) -> Dict[str, bool]:
        """Validate parsed data"""
        pass


class BaseVerifier(ABC):
    """Base class for all verifiers"""

    def __init__(self, config: PluginConfig):
        self.config = config

    @abstractmethod
    def can_verify(self, content_type: str) -> bool:
        """Check if this verifier can handle the given content type"""
        pass

    @abstractmethod
    def verify(self, scan_result: ScanResult) -> Dict[str, bool]:
        """Verify the scan result"""
        pass


class BasePlugin(ABC):
    """Base class for all plugins"""

    def __init__(self, config: PluginConfig):
        self.config = config
        self.parsers: List[BaseParser] = []
        self.verifiers: List[BaseVerifier] = []

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass

    def get_parsers(self) -> List[BaseParser]:
        """Get all parsers provided by this plugin"""
        return self.parsers

    def get_verifiers(self) -> List[BaseVerifier]:
        """Get all verifiers provided by this plugin"""
        return self.verifiers

    def get_config(self) -> PluginConfig:
        """Get plugin configuration"""
        return self.config


class PluginManager:
    """Manages plugin loading and execution"""

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.parsers: List[BaseParser] = []
        self.verifiers: List[BaseVerifier] = []

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a new plugin"""
        try:
            if plugin.initialize():
                self.plugins[plugin.config.name] = plugin
                self.parsers.extend(plugin.get_parsers())
                self.verifiers.extend(plugin.get_verifiers())
                return True
        except Exception as e:
            print(f"Failed to register plugin {plugin.config.name}: {e}")
        return False

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.cleanup()
            del self.plugins[plugin_name]

            # Remove parsers and verifiers
            self.parsers = [p for p in self.parsers if p not in plugin.get_parsers()]
            self.verifiers = [
                v for v in self.verifiers if v not in plugin.get_verifiers()
            ]
            return True
        return False

    def get_parser_for_content(self, content: str) -> Optional[BaseParser]:
        """Get the appropriate parser for given content"""
        for parser in self.parsers:
            if parser.can_parse(content):
                return parser
        return None

    def get_verifiers_for_content_type(self, content_type: str) -> List[BaseVerifier]:
        """Get all verifiers that can handle the given content type"""
        return [v for v in self.verifiers if v.can_verify(content_type)]

    def parse_content(self, content: str) -> Optional[ScanResult]:
        """Parse content using appropriate parser"""
        parser = self.get_parser_for_content(content)
        if parser:
            return parser.parse(content)
        return None

    def verify_scan_result(self, scan_result: ScanResult) -> Dict[str, bool]:
        """Verify scan result using appropriate verifiers"""
        verifiers = self.get_verifiers_for_content_type(scan_result.content_type)
        verification_results = {}

        for verifier in verifiers:
            try:
                results = verifier.verify(scan_result)
                verification_results.update(results)
            except Exception as e:
                print(f"Verification failed for {verifier.__class__.__name__}: {e}")

        return verification_results

    def get_plugin_info(self) -> List[Dict[str, Any]]:
        """Get information about all registered plugins"""
        return [
            {
                "name": plugin.config.name,
                "version": plugin.config.version,
                "description": plugin.config.description,
                "author": plugin.config.author,
                "enabled": plugin.config.enabled,
                "parsers_count": len(plugin.get_parsers()),
                "verifiers_count": len(plugin.get_verifiers()),
            }
            for plugin in self.plugins.values()
        ]

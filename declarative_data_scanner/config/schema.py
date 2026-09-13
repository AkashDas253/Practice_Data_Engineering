from pydantic import BaseModel, ConfigDict, Field


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    path: str | None = None


class DiscoveryConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    config: dict[str, object] = Field(default_factory=dict)


class ReaderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    config: dict[str, object] = Field(default_factory=dict)


class ParserModuleConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    config: dict[str, object] = Field(default_factory=dict)


class ParserConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modules: list[ParserModuleConfig] = Field(default_factory=list)


class ProcessingModuleConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    config: dict[str, object] = Field(default_factory=dict)


class ProcessingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modules: list[ProcessingModuleConfig] = Field(default_factory=list)


class OutputConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    config: dict[str, object] = Field(default_factory=dict)


class StateConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    path: str | None = None


class ScanConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: SourceConfig
    discovery: DiscoveryConfig
    reader: ReaderConfig
    parser: ParserConfig
    processing: ProcessingConfig = Field(
        default_factory=ProcessingConfig
    )
    output: OutputConfig
    state: StateConfig = Field(
        default_factory=StateConfig
    )


class ApplicationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scans: dict[str, ScanConfig]

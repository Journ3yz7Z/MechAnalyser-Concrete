import dataclasses
import mech_analyser.experiment.collation as ma_collation
import mech_analyser.experiment.data as ma_data
import mech_analyser.experiment.ui as ma_ui


class Registry:
    """
    A registry to hold and manage experiment components.
    """

    @dataclasses.dataclass(frozen=True)
    class Key:
        """
        Registry key comprised of the instrument and experiment.

        Args:
            instrument: The instrument to which the registry element belongs.
            experiment: The experiment to which the registry element belongs.
        """

        instrument: str
        experiment: str

    @dataclasses.dataclass
    class Value:
        """
        Registry value comprised of the instrument and experiment components.

        Args:
            widget: The configuration widget.
            raw_transcoder: The raw data transcoder.
            processed_transcoder: The processed data transcoder.
            summary_transcoder: The summary data transcoder.
            raw_collation_transcoder: The raw data collation transcoder.
            summary_collation_transcoder: The summary data collation transcoder.
            summary_collation_type: The type of summary collation.
        """

        widget: ma_ui.ConfigWidget
        raw_transcoder: ma_data.RawTranscoder
        processed_transcoder: ma_data.ProcessedTranscoder
        summary_transcoder: ma_data.SummaryTranscoder
        raw_collation_transcoder: ma_collation.RawTranscoder
        summary_collation_transcoder: ma_collation.SummaryTranscoder
        summary_collation_type: type[ma_collation.SummaryCollation]

    def __init__(self) -> None:
        self._registry: dict[Registry.Key, Registry.Value] = {}
        self._desktop_factories = {}

    def add_desktop(self, name, factory):
        """Register a single-specimen workspace without the CSV batch contract."""
        if name in self._desktop_factories:
            raise KeyError("Desktop workspace already registered")
        self._desktop_factories[name] = factory

    def create_desktop(self, name):
        return self._desktop_factories[name]()

    @classmethod
    def desktop_registry(cls):
        import importlib
        from mech_analyser.config import EXPERIMENT_MODULES
        registry = cls()
        for path in EXPERIMENT_MODULES:
            module = importlib.import_module(path)
            if getattr(module, "SINGLE_SAMPLE", False):
                registry.add_desktop(module.EXPERIMENT, module.create_workspace)
        return registry

    def get_experiments(self, instrument: str) -> list[str]:
        """
        Obtains the list of experiments associated with the specified instrument that are
        stored within the registry.

        Args:
            instrument: The instrument for which to obtain the list of associated
                experiments.

        Returns:
            list[str]: A list of experiments associated with the specified instrument that
                are stored within the registry.
        """

        experiments: list[str] = [
            key.experiment for key in self._registry if key.instrument == instrument
        ]
        experiments.sort()

        return experiments

    def get_instruments(self) -> list[str]:
        """
        Obtains the list of recognised instruments that are stored within the registry.

        Returns:
            list[str]: The list of recognised instruments that are stored within the
                registry.
        """

        instruments: list[str] = list(set([key.instrument for key in self._registry]))
        instruments.sort()

        return instruments

    def get(self, key: Key) -> Value:
        """
        Obtains the experiment components associated with the specified instrument and
        experiment.

        Args:
            key: The instrument and experiment for which to obtain the components.

        Raises:
            KeyError: If the instrument and experiment is not stored within the registry.

        Returns:
            The components associated with the specified instrument and experiment.
        """

        return self._registry[key]

    def get_processed_transcoder(self, key: Key) -> ma_data.ProcessedTranscoder:
        """
        Obtains the processed data transcoder associated with the specified instrument and
        experiment.

        Args:
            key: The instrument and experiment for which to obtain the processed data
                transcoder.

        Raises:
            KeyError: If the instrument and experiment is not stored within the registry.

        Returns:
            ProcessedTranscoder: The processed data transcoder associated with the
                specified instrument and experiment.
        """

        return self._registry[key].processed_transcoder

    def get_raw_collation_transcoder(self, key: Key) -> ma_collation.RawTranscoder:
        """
        Obtains the raw data collation transcoder associated with the specified instrument
        and experiment.

        Args:
            key: The instrument and experiment for which to obtain the raw data collation
                transcoder.

        Raises:
            KeyError: If the instrument and experiment is not stored within the registry.

        Returns:
            RawTranscoder: The raw data collation transcoder associated with the specified
                instrument and experiment.
        """

        return self._registry[key].raw_collation_transcoder

    def get_raw_transcoder(self, key: Key) -> ma_data.RawTranscoder:
        """
        Obtains the raw data transcoder associated with the specified instrument and
        experiment.

        Args:
            key: The instrument and experiment for which to obtain the raw data
                transcoder.

        Raises:
            KeyError: If the instrument and experiment is not stored within the registry.

        Returns:
            RawTranscoder: The raw data transcoder associated with the specified instrument
                and experiment.
        """

        return self._registry[key].raw_transcoder

    def get_summary_collation_transcoder(
        self, key: Key
    ) -> ma_collation.SummaryTranscoder:
        """
        Obtains the summary data collation transcoder associated with the specified
        instrument and experiment.

        Args:
            key: The instrument and experiment for which to obtain the summary data
                collation transcoder.

        Raises:
            KeyError: If the instrument and experiment is not stored within the registry.

        Returns:
            SummaryTranscoder: The summary data collation transcoder associated with the
                specified instrument and experiment.
        """

        return self._registry[key].summary_collation_transcoder

    def get_summary_collation_type(self, key: Key) -> type[ma_collation.SummaryCollation]:
        """
        Obtains the type of summary collation associated with the specified instrument and
        experiment.

        Args:
            key: The instrument and experiment for which to obtain the type of summary
                collation.

        Raises:
            KeyError: If the instrument and experiment is not stored within the registry.

        Returns:
            type[SummaryCollation]: The type of summary collation associated with the
                specified instrument and experiment.
        """

        return self._registry[key].summary_collation_type

    def get_summary_transcoder(self, key: Key) -> ma_data.SummaryTranscoder:
        """
        Obtains the summary data transcoder associated with the specified instrument and
        experiment.

        Args:
            key: The instrument and experiment for which to obtain the summary data
                transcoder.

        Raises:
            KeyError: If the instrument and experiment is not stored within the registry.

        Returns:
            SummaryTranscoder: The summary data transcoder associated with the specified
                instrument and experiment.
        """

        return self._registry[key].summary_transcoder

    def get_widget(self, key: Key) -> ma_ui.ConfigWidget:
        """
        Obtains the configuration widget associated with the specified instrument and
        experiment.

        Args:
            key: The instrument and experiment for which to obtain the configuration
                widget.

        Raises:
            KeyError: If the instrument and experiment is not stored within the registry.

        Returns:
            ConfigWidget: The configuration widget associated with the specified instrument
                and experiment.
        """

        return self._registry[key].widget

    def add(self, key: Key, value: Value) -> None:
        """
        Adds the experiment components to the registry.

        Args:
            key: The instrument and experiment with which to associate the components.
            value: The experiment components.
        """

        if key in self._registry:
            raise KeyError("Key already exists")

        self._registry[key] = value

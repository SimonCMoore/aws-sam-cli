from unittest import TestCase
from unittest.mock import MagicMock, patch

from samcli.lib.sync.sync_flow_factory import SyncFlowFactory


class TestSyncFlowFactory(TestCase):
    def create_factory(self):
        factory = SyncFlowFactory(
            build_context=MagicMock(), deploy_context=MagicMock(), stacks=[MagicMock(), MagicMock()]
        )
        return factory

    @patch("samcli.lib.sync.sync_flow_factory.get_physical_id_mapping")
    @patch("samcli.lib.sync.sync_flow_factory.get_boto_resource_provider_with_config")
    def test_load_physical_id_mapping(self, get_boto_resource_provider_mock, get_physical_id_mapping_mock):
        get_physical_id_mapping_mock.return_value = {"Resource1": "PhysicalResource1", "Resource2": "PhysicalResource2"}

        factory = self.create_factory()
        factory.load_physical_id_mapping()

        self.assertEqual(len(factory._physical_id_mapping), 2)
        self.assertEqual(
            factory._physical_id_mapping, {"Resource1": "PhysicalResource1", "Resource2": "PhysicalResource2"}
        )

    @patch("samcli.lib.sync.sync_flow_factory.ImageFunctionSyncFlow")
    @patch("samcli.lib.sync.sync_flow_factory.ZipFunctionSyncFlow")
    def test_create_lambda_flow_zip(self, zip_function_mock, image_function_mock):
        factory = self.create_factory()
        resource = {"Properties": {"PackageType": "Zip"}}
        result = factory._create_lambda_flow("Function1", resource)
        self.assertEqual(result, zip_function_mock.return_value)

    @patch("samcli.lib.sync.sync_flow_factory.ImageFunctionSyncFlow")
    @patch("samcli.lib.sync.sync_flow_factory.ZipFunctionSyncFlow")
    def test_create_lambda_flow_image(self, zip_function_mock, image_function_mock):
        factory = self.create_factory()
        resource = {"Properties": {"PackageType": "Image"}}
        result = factory._create_lambda_flow("Function1", resource)
        self.assertEqual(result, image_function_mock.return_value)

    @patch("samcli.lib.sync.sync_flow_factory.LayerSyncFlow")
    def test_create_layer_flow(self, layer_sync_mock):
        factory = self.create_factory()
        result = factory._create_layer_flow("Layer1", {})
        self.assertEqual(result, layer_sync_mock.return_value)

    @patch("samcli.lib.sync.sync_flow_factory.ImageFunctionSyncFlow")
    @patch("samcli.lib.sync.sync_flow_factory.ZipFunctionSyncFlow")
    def test_create_lambda_flow_other(self, zip_function_mock, image_function_mock):
        factory = self.create_factory()
        resource = {"Properties": {"PackageType": "Other"}}
        result = factory._create_lambda_flow("Function1", resource)
        self.assertEqual(result, None)

    @patch("samcli.lib.sync.sync_flow_factory.RestApiSyncFlow")
    def test_create_rest_api_flow(self, rest_api_sync_mock):
        factory = self.create_factory()
        result = factory._create_rest_api_flow("API1", {})
        self.assertEqual(result, rest_api_sync_mock.return_value)

    @patch("samcli.lib.sync.sync_flow_factory.HttpApiSyncFlow")
    def test_create_api_flow(self, http_api_sync_mock):
        factory = self.create_factory()
        result = factory._create_api_flow("API1", {})
        self.assertEqual(result, http_api_sync_mock.return_value)

    @patch("samcli.lib.sync.sync_flow_factory.get_resource_by_id")
    def test_create_sync_flow(self, get_resource_by_id_mock):
        factory = self.create_factory()

        sync_flow = MagicMock()
        resource_identifier = MagicMock()
        get_resource_by_id = MagicMock()
        get_resource_by_id_mock.return_value = get_resource_by_id
        generator_mock = MagicMock()
        generator_mock.return_value = sync_flow

        get_generator_function_mock = MagicMock()
        get_generator_function_mock.return_value = generator_mock
        factory._get_generator_function = get_generator_function_mock

        result = factory.create_sync_flow(resource_identifier)

        self.assertEqual(result, sync_flow)
        generator_mock.assert_called_once_with(factory, resource_identifier, get_resource_by_id)

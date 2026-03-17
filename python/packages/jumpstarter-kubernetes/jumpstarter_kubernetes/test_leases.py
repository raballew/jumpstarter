from unittest.mock import MagicMock, patch

from kubernetes_asyncio.client.models import V1Condition, V1ObjectMeta, V1ObjectReference

from jumpstarter_kubernetes import V1Alpha1Lease, V1Alpha1LeaseSelector, V1Alpha1LeaseSpec, V1Alpha1LeaseStatus

TEST_LEASE = V1Alpha1Lease(
    api_version="jumpstarter.dev/v1alpha1",
    kind="Lease",
    metadata=V1ObjectMeta(
        creation_timestamp="2021-10-01T00:00:00Z",
        generation=1,
        name="test-lease",
        namespace="default",
        resource_version="1",
        uid="7a25eb81-6443-47ec-a62f-50165bffede8",
    ),
    spec=V1Alpha1LeaseSpec(
        client=V1ObjectReference(name="test-client"),
        duration="1h",
        selector=V1Alpha1LeaseSelector(match_labels={"test": "label", "another": "something"}),
    ),
    status=V1Alpha1LeaseStatus(
        begin_time="2021-10-01T00:00:00Z",
        conditions=[
            V1Condition(
                last_transition_time="2021-10-01T00:00:00Z", status="True", type="Active", message="", reason=""
            )
        ],
        end_time="2021-10-01T01:00:00Z",
        ended=False,
        exporter=V1ObjectReference(name="test-exporter"),
    ),
)


def test_lease_dump_json():
    assert (
        TEST_LEASE.dump_json()
        == """{
    "apiVersion": "jumpstarter.dev/v1alpha1",
    "kind": "Lease",
    "metadata": {
        "creationTimestamp": "2021-10-01T00:00:00Z",
        "generation": 1,
        "name": "test-lease",
        "namespace": "default",
        "resourceVersion": "1",
        "uid": "7a25eb81-6443-47ec-a62f-50165bffede8"
    },
    "spec": {
        "client": {
            "name": "test-client"
        },
        "duration": "1h",
        "selector": {
            "matchLabels": {
                "test": "label",
                "another": "something"
            }
        }
    },
    "status": {
        "beginTime": "2021-10-01T00:00:00Z",
        "conditions": [
            {
                "lastTransitionTime": "2021-10-01T00:00:00Z",
                "message": "",
                "reason": "",
                "status": "True",
                "type": "Active"
            }
        ],
        "endTime": "2021-10-01T01:00:00Z",
        "ended": false,
        "exporter": {
            "name": "test-exporter"
        }
    }
}"""
    )


def test_lease_dump_yaml():
    assert (
        TEST_LEASE.dump_yaml()
        == """apiVersion: jumpstarter.dev/v1alpha1
kind: Lease
metadata:
  creationTimestamp: '2021-10-01T00:00:00Z'
  generation: 1
  name: test-lease
  namespace: default
  resourceVersion: '1'
  uid: 7a25eb81-6443-47ec-a62f-50165bffede8
spec:
  client:
    name: test-client
  duration: 1h
  selector:
    matchLabels:
      another: something
      test: label
status:
  beginTime: '2021-10-01T00:00:00Z'
  conditions:
  - lastTransitionTime: '2021-10-01T00:00:00Z'
    message: ''
    reason: ''
    status: 'True'
    type: Active
  endTime: '2021-10-01T01:00:00Z'
  ended: false
  exporter:
    name: test-exporter
"""
    )


def test_lease_rich_add_columns_default():
    mock_table = MagicMock()
    V1Alpha1Lease.rich_add_columns(mock_table)
    assert mock_table.add_column.call_count == 4
    mock_table.add_column.assert_any_call("NAME", no_wrap=True)
    mock_table.add_column.assert_any_call("CLIENT")
    mock_table.add_column.assert_any_call("EXPORTER")
    mock_table.add_column.assert_any_call("REMAINING")


def test_lease_rich_add_columns_wide():
    mock_table = MagicMock()
    V1Alpha1Lease.rich_add_columns(mock_table, output="wide")
    assert mock_table.add_column.call_count == 10
    mock_table.add_column.assert_any_call("NAME", no_wrap=True)
    mock_table.add_column.assert_any_call("CLIENT")
    mock_table.add_column.assert_any_call("SELECTOR")
    mock_table.add_column.assert_any_call("EXPORTER")
    mock_table.add_column.assert_any_call("DURATION")
    mock_table.add_column.assert_any_call("STATUS")
    mock_table.add_column.assert_any_call("REASON")
    mock_table.add_column.assert_any_call("BEGIN")
    mock_table.add_column.assert_any_call("END")
    mock_table.add_column.assert_any_call("AGE")


def test_lease_rich_add_rows_default():
    mock_table = MagicMock()
    with patch("jumpstarter_kubernetes.leases.time_remaining", return_value="30m"):
        TEST_LEASE.rich_add_rows(mock_table)
    args = mock_table.add_row.call_args[0]
    assert len(args) == 4
    assert args[0] == "test-lease"
    assert args[1] == "test-client"
    assert args[2] == "test-exporter"
    assert args[3] == "30m"


def test_lease_rich_add_rows_wide():
    mock_table = MagicMock()
    with patch("jumpstarter_kubernetes.leases.time_since", return_value="5m"):
        TEST_LEASE.rich_add_rows(mock_table, output="wide")
    args = mock_table.add_row.call_args[0]
    assert len(args) == 10
    assert args[0] == "test-lease"
    assert args[1] == "test-client"
    assert args[2] == "test:label,another:something"
    assert args[3] == "test-exporter"
    assert args[4] == "1h"
    assert args[5] == "InProgress"


def test_lease_rich_add_rows_pending_displays_dash():
    pending_lease = V1Alpha1Lease(
        api_version="jumpstarter.dev/v1alpha1",
        kind="Lease",
        metadata=V1ObjectMeta(
            creation_timestamp="2021-10-01T00:00:00Z",
            generation=1,
            name="pending-lease",
            namespace="default",
            resource_version="1",
            uid="7a25eb81-6443-47ec-a62f-50165bffede8",
        ),
        spec=V1Alpha1LeaseSpec(
            client=V1ObjectReference(name="test-client"),
            duration="1h",
            selector=V1Alpha1LeaseSelector(match_labels={}),
        ),
        status=V1Alpha1LeaseStatus(
            begin_time=None,
            conditions=[],
            end_time=None,
            ended=False,
            exporter=None,
        ),
    )
    mock_table = MagicMock()
    with patch("jumpstarter_kubernetes.leases.time_remaining", return_value="-"):
        pending_lease.rich_add_rows(mock_table)
    args = mock_table.add_row.call_args[0]
    assert args[3] == "-"


def test_lease_from_dict_without_match_labels_name_targeted():
    lease = V1Alpha1Lease.from_dict(
        {
            "apiVersion": "jumpstarter.dev/v1alpha1",
            "kind": "Lease",
            "metadata": {
                "creationTimestamp": "2021-10-01T00:00:00Z",
                "generation": 1,
                "managedFields": [],
                "name": "test-lease",
                "namespace": "default",
                "resourceVersion": "1",
                "uid": "7a25eb81-6443-47ec-a62f-50165bffede8",
            },
            "spec": {
                "clientRef": {"name": "test-client"},
                "duration": "1h",
                "selector": {},
                "exporterRef": {"name": "test-exporter"},
            },
            "status": {
                "ended": False,
                "conditions": [
                    {
                        "lastTransitionTime": "2021-10-01T00:00:00Z",
                        "message": "",
                        "observedGeneration": 1,
                        "reason": "",
                        "status": "True",
                        "type": "Active",
                    }
                ],
            },
        }
    )

    assert lease.spec.selector.match_labels == {}

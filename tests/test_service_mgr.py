"""Test ServiceManager and ServiceTableModel."""
import pytest
from lintask.core.service_mgr import ServiceManager
from lintask.models.service_item import ServiceItem
from lintask.models.service_model import ServiceTableModel, ServiceFilterProxyModel


def test_service_item_properties():
    s1 = ServiceItem("ssh.service", "loaded", "active", "running", "OpenBSD SSH daemon")
    assert s1.is_running is True
    assert s1.is_failed is False

    s2 = ServiceItem("cups.service", "loaded", "failed", "failed", "CUPS Scheduler")
    assert s2.is_running is False
    assert s2.is_failed is True


def test_service_table_model():
    model = ServiceTableModel()
    test_data = [
        ServiceItem("bluetooth.service", "loaded", "active", "running", "Bluetooth Service"),
        ServiceItem("docker.service", "loaded", "inactive", "dead", "Docker App Engine"),
        ServiceItem("nginx.service", "loaded", "failed", "failed", "Nginx Web Server"),
    ]

    model.update_services(test_data)
    assert model.rowCount() == 3
    assert model.columnCount() == 5

    s = model.get_service_at(0)
    assert s is not None
    assert s.name == "bluetooth.service"


def test_service_filter_proxy():
    model = ServiceTableModel()
    proxy = ServiceFilterProxyModel()
    proxy.setSourceModel(model)

    test_data = [
        ServiceItem("bluetooth.service", "loaded", "active", "running", "Bluetooth Service"),
        ServiceItem("docker.service", "loaded", "inactive", "dead", "Docker App Engine"),
        ServiceItem("nginx.service", "loaded", "failed", "failed", "Nginx Web Server"),
    ]

    model.update_services(test_data)
    assert proxy.rowCount() == 3

    # Filter by search query
    proxy.set_filter_query("dock")
    assert proxy.rowCount() == 1

    proxy.set_filter_query("web server")
    assert proxy.rowCount() == 1

    # Filter by status
    proxy.set_filter_query("")
    proxy.set_status_filter("active")
    assert proxy.rowCount() == 1

    proxy.set_status_filter("failed")
    assert proxy.rowCount() == 1

    proxy.set_status_filter("all")
    assert proxy.rowCount() == 3


def test_service_manager_scan_safe():
    mgr = ServiceManager()
    services = mgr.scan_services()
    assert isinstance(services, list)


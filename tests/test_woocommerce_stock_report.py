from unittest import TestCase

from BackEnd.services.woocommerce_service import WooCommerceService


class _FakeResponse:
    def __init__(self, status_code, payload, headers=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._payload


class _FakeAPI:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, endpoint, params=None):
        self.calls.append((endpoint, params))
        return self.responses.pop(0)


class WooCommerceStockReportTests(TestCase):
    def test_stock_report_fetches_published_products_without_invalid_stock_status_param(self):
        service = WooCommerceService.__new__(WooCommerceService)
        service.wcapi = _FakeAPI(
            [
                _FakeResponse(
                    200,
                    [
                        {
                            "id": 1,
                            "name": "Black Wallet",
                            "sku": "BW-1",
                            "stock_status": "instock",
                            "stock_quantity": 9,
                            "price": "850",
                            "categories": [{"name": "Accessories"}],
                            "manage_stock": True,
                            "type": "simple",
                        }
                    ],
                    headers={"x-wp-totalpages": "1"},
                )
            ]
        )

        df = service.get_stock_report()

        self.assertEqual(len(df), 1)
        self.assertEqual(service.wcapi.calls[0][0], "products")
        self.assertEqual(service.wcapi.calls[0][1]["status"], "publish")
        self.assertNotIn("stock_status", service.wcapi.calls[0][1])
        self.assertEqual(df.loc[0, "Stock Status"], "instock")
        self.assertEqual(df.loc[0, "Stock Quantity"], 9)

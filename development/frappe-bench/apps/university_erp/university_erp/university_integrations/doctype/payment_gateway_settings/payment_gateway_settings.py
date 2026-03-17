# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url


class PaymentGatewaySettings(Document):
    def validate(self):
        self.set_webhook_url()
        self.validate_gateway_credentials()

    def set_webhook_url(self):
        """Set the webhook URL based on site URL"""
        base_url = get_url()
        self.webhook_url = f"{base_url}/api/method/university_erp.university_integrations.payment_gateway.razorpay_webhook"

    def validate_gateway_credentials(self):
        """Validate that required credentials are set for selected gateway"""
        if not self.default_gateway:
            return

        if self.default_gateway == "Razorpay":
            if not self.razorpay_key_id or not self.razorpay_key_secret:
                frappe.msgprint(
                    "Razorpay Key ID and Secret are required for Razorpay gateway",
                    indicator="orange",
                    alert=True
                )

        elif self.default_gateway == "PayU":
            if not self.payu_merchant_key or not self.payu_merchant_salt:
                frappe.msgprint(
                    "Merchant Key and Salt are required for PayU gateway",
                    indicator="orange",
                    alert=True
                )

        elif self.default_gateway == "Stripe":
            if not self.stripe_publishable_key or not self.stripe_secret_key:
                frappe.msgprint(
                    "Publishable Key and Secret Key are required for Stripe gateway",
                    indicator="orange",
                    alert=True
                )

    def get_razorpay_client(self):
        """Get Razorpay client instance"""
        try:
            import razorpay
            return razorpay.Client(
                auth=(self.razorpay_key_id, self.get_password("razorpay_key_secret"))
            )
        except ImportError:
            frappe.throw("Razorpay library not installed. Run: pip install razorpay")
        except Exception as e:
            frappe.throw(f"Failed to initialize Razorpay client: {str(e)}")

    def get_stripe_client(self):
        """Get Stripe client instance"""
        try:
            import stripe
            stripe.api_key = self.get_password("stripe_secret_key")
            return stripe
        except ImportError:
            frappe.throw("Stripe library not installed. Run: pip install stripe")
        except Exception as e:
            frappe.throw(f"Failed to initialize Stripe client: {str(e)}")


@frappe.whitelist()
def test_gateway_connection(gateway=None):
    """Test connection to payment gateway"""
    settings = frappe.get_single("Payment Gateway Settings")
    gateway = gateway or settings.default_gateway

    try:
        if gateway == "Razorpay":
            client = settings.get_razorpay_client()
            # Test by fetching orders (should return empty list or orders)
            client.order.all({"count": 1})
            return {"success": True, "message": "Razorpay connection successful"}

        elif gateway == "Stripe":
            stripe = settings.get_stripe_client()
            # Test by fetching balance
            stripe.Balance.retrieve()
            return {"success": True, "message": "Stripe connection successful"}

        else:
            return {"success": False, "message": f"Test not implemented for {gateway}"}

    except Exception as e:
        return {"success": False, "message": str(e)}

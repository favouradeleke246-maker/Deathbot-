from modules.wa_delivery_fingerprint import WaDeliveryFingerprint

class Verify:
    @staticmethod
    def check_whatsapp_registration(phone):
        return WaDeliveryFingerprint().exploit(phone)

from typing import Optional

class DeviceClient:
    def __init__(self, device_id: Optional[int]):
        self.device_id = device_id

    async def run_command(self, command: Optional[str]) -> str:
        # Stub implementation: echo back command
        return f"Executed command on device {self.device_id}: {command or '<none>'}"

    async def backup_config(self) -> str:
        # Stub config text
        return f"! backup config for device {self.device_id}\nhostname device-{self.device_id}\nend\n"

    async def restore_config(self, config_text: str) -> str:
        # Stub restore
        return f"Restored config on device {self.device_id}, length={len(config_text)}"

from auditor import Auditor
from publisher import Publisher
import tkinter as tk
from tkinter import ttk
import json
import time


class App(tk.Frame):
    """Verify and publish trade signals on the Ethereum blockchain.

    Main.py is a GUI for accessing the functionality of publisher.py and
    auditor.py modules. Auditor.py and Publisher.py modules could be integrated
    into existing financial systems or trading software (minus this GUI)."""

    # Set true to run on Eth mainnet, otherwise run on Ropsten testnet.
    LIVE = False

    # Ethereum node endpoints.
    TESTNET = ""
    MAINNET = ""

    # Ethereum public address and private key.
    pub_k = ""
    pvt_k = ""

    # Get one at https://etherscan.io.
    ETHERSCAN_API_TOKEN = ""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Set Eth node endpoint.
        if self.LIVE:
            self.endpoint = self.MAINNET
        else:
            self.endpoint = self.TESTNET

        # Load data.json signal dict.
        with open("data.json") as file:
            self.data = json.load(file)

        # Init component modules.
        self.auditor = Auditor(
            self.endpoint,
            self.data,
            self.ETHERSCAN_API_TOKEN,
            self.LIVE)
        self.publisher = Publisher(
            self.endpoint,
            self.pub_k,
            self.pvt_k,
            self.data)

        self.init_gui()

        # Check if address and key are valid
        self.output.insert(
            self.output.size() + 1,
            "Address check: " + str(self.auditor.validate(self.pub_k)))

        self.output.insert(
            self.output.size() + 1,
            "Private key check: " + str(self.auditor.validate(self.pvt_k)))

    def publish(self):
        """Publish signal composed from gui combobox inputs to Ethereum,
        then print results and tx hash in the output pane."""

        # No need to check address & key as they are validated at init.
        # Signal is formed from combobox value strings
        signal = [
            self.instrumentcbb.get(),
            self.insttypecbb.get(),
            self.exchangecbb.get(),
            self.strategycbb.get(),
            self.directioncbb.get(),
            self.order_typecbb.get(),
            self.misccbb.get(),
            self.triggercbb.get()]

        # Print params to output pane
        self.output.insert(
            self.output.size() + 1,
            "Raw signal: " + str(signal))

        # Encode param strings
        encoded = self.publisher.encode(signal)
        self.output.insert(
            self.output.size() + 1,
            "Encoded signal: " + str(encoded))

        # Publish and print hash
        txhash = self.publisher.publish(encoded)
        self.output.insert(
            self.output.size() + 1,
            "Published signal. Tx hash: " + str(txhash))

    def audit(self):
        """Scrape and audit tx's using address parameter from addr_field
        then print the results in the output pane."""

        # Double check address is valid.
        address = self.addr_field.get()
        if not self.auditor.validate(address) == "Valid":
            self.output.insert(
                self.output.size() + 1, "Invalid address.")
        # Print to ouput pane
        result = self.auditor.scrape(address)
        if result:
            # First print the raw signal
            self.output.insert(
                self.output.size() + 1, str(len(result)) +
                " encoded signals found at " + str(address) + ":")
            for i in result:
                self.output.insert(
                    self.output.size() + 1,
                    i)

            # Now print decoded human-readable signals
            decoded = self.auditor.decode(result)
            self.output.insert(
                self.output.size() + 1,
                "Decoded signal output:")
            for i in decoded:
                self.output.insert(
                    self.output.size() + 1,
                    i)
        else:
            self.output.insert(
                self.output.size() + 1,
                str("No signals present for address " + address + "."))
            pass

    def to_clipboard(self, item):
        """Write the given object to system clipboard."""

        c = tk.Tk()
        c.withdraw()
        c.clipboard_clear()
        c.clipboard_append(item)
        c.update()
        c.destroy()

    def init_gui(self):
        """Init gui components."""

        # left panel upper (input panel)
        self.input = tk.Frame(self, width=430)
        self.input_upper = tk.Frame(self.input, width=430, height=320)
        self.input_lower = tk.Frame(self.input, width=430)

        self.title_label_upper = tk.Label(
            self.input_upper,
            text="Search an Ethereum address for encoded signals:",
            font=('', 11, 'bold'))
        self.pub_k_label = tk.Label(
            self.input_upper, text="Your ETH address is " + self.pub_k)

        pvt_preview = self.pvt_k[:8] + "...." + self.pvt_k[-8:]
        self.pvt_k_label = tk.Label(
            self.input_upper, text="Your ETH private key is " + pvt_preview + "  (withheld for security)")  # noqa
        self.addr_field = tk.Entry(self.input_upper, width=50)
        self.addr_field.insert(0, self.pub_k)
        self.addr_label = tk.Label(
            self.input_upper, text="Originating address:")
        self.spacing_label = tk.Label(self.input_upper, text=" ")

        self.audit_button = tk.Button(
            self.input_upper,
            text="  Audit  ",
            command=self.audit)

        self.copy_pub_k_button = tk.Button(
            self.input_upper,
            text="  Copy  ",
            command=lambda: self.to_clipboard(self.pub_k))

        self.copy_pvt_k_button = tk.Button(
            self.input_upper,
            text="  Copy  ",
            command=lambda: self.to_clipboard(self.pvt_k))

        self.title_label_upper.grid(row=0, columnspan=5)
        self.addr_label.grid(row=1, column=0, columnspan=1, sticky="w")
        self.addr_field.grid(row=1, column=1, columnspan=2, pady=10)
        self.spacing_label.grid(row=1, column=4, columnspan=1)
        self.audit_button.grid(row=1, column=5, columnspan=1, sticky="e")
        self.pub_k_label.grid(row=2, columnspan=3, sticky="w", pady=20)
        self.pvt_k_label.grid(row=3, columnspan=3, sticky="w")
        self.copy_pub_k_button.grid(row=2, column=5, columnspan=1, sticky="w")
        self.copy_pvt_k_button.grid(row=3, column=5, columnspan=1, sticky="w")

        # Left panel lower (input panel)
        self.title_label_lower = tk.Label(
            self.input_lower,
            text="Publish trade signals to your Ethereum address:",
            font=('', 11, 'bold'))

        self.instrument_label = tk.Label(
            self.input_lower, text="Instrument:")
        self.instrumentcbb = ttk.Combobox(
            self.input_lower,
            state="readonly",
            values=list(
                self.data['data']['instrument'].values()), width=55)
        self.instrumentcbb.current(0)

        self.insttype_label = tk.Label(
            self.input_lower, text="Instrument type:")
        self.insttypecbb = ttk.Combobox(
            self.input_lower,
            state="readonly",
            values=list(
                self.data['data']['inst_type'].values()), width=55)
        self.insttypecbb.current(3)

        self.exchange_label = tk.Label(
            self.input_lower, text="Exchange:")
        self.exchangecbb = ttk.Combobox(
            self.input_lower,
            state="readonly",
            values=list(
                self.data['data']['exchange'].values()), width=55)
        self.exchangecbb.current(0)

        self.strategy_label = tk.Label(
            self.input_lower, text="Strategy:")
        self.strategycbb = ttk.Combobox(
            self.input_lower,
            state="readonly",
            values=list(
                self.data['data']['strategy'].values()), width=55)
        self.strategycbb.current(2)

        self.direction_label = tk.Label(
            self.input_lower, text="Direction:")
        self.directioncbb = ttk.Combobox(
            self.input_lower,
            state="readonly",
            values=list(
                self.data['data']['direction'].values()), width=55)
        self.directioncbb.current(0)

        self.order_type_label = tk.Label(
            self.input_lower, text="Order type:")
        self.order_typecbb = ttk.Combobox(
            self.input_lower,
            state="readonly",
            values=list(
                self.data['data']['order_type'].values()), width=55)
        self.order_typecbb.current(2)

        self.misc_label = tk.Label(
            self.input_lower, text="Misc:")
        self.misccbb = ttk.Combobox(
            self.input_lower,
            state="readonly",
            values=list(
                self.data['data']['misc'].values()), width=55)
        self.misccbb.current(1)

        self.trigger_label = tk.Label(
            self.input_lower, text="Trigger:")
        self.triggercbb = ttk.Combobox(
            self.input_lower,
            state="readonly",
            values=list(
                self.data['data']['trigger'].values()), width=55)
        self.triggercbb.current(0)

        self.publish_button = tk.Button(
            self.input_lower,
            text="  Publish Signal  ",
            width=20,
            command=self.publish)

        self.title_label_lower.grid(row=0, columnspan=5, pady=5)
        self.instrument_label.grid(row=1, column=0, columnspan=1, sticky="w")
        self.instrumentcbb.grid(row=1, column=2, columnspan=3)
        self.insttype_label.grid(row=2, column=0, columnspan=1, sticky="w")
        self.insttypecbb.grid(row=2, column=2, columnspan=3)
        self.exchange_label.grid(row=3, column=0, columnspan=1, sticky="w")
        self.exchangecbb.grid(row=3, column=2, columnspan=3)
        self.strategy_label.grid(row=4, column=0, columnspan=1, sticky="w")
        self.strategycbb.grid(row=4, column=2, columnspan=3)
        self.strategy_label.grid(row=5, column=0, columnspan=1, sticky="w")
        self.strategycbb.grid(row=5, column=2, columnspan=3)
        self.direction_label.grid(row=6, column=0, columnspan=1, sticky="w")
        self.directioncbb.grid(row=6, column=2, columnspan=3)
        self.order_type_label.grid(row=7, column=0, columnspan=1, sticky="w")
        self.order_typecbb.grid(row=7, column=2, columnspan=3)
        self.misc_label.grid(row=8, column=0, columnspan=1, sticky="w")
        self.misccbb.grid(row=8, column=2, columnspan=3)
        self.trigger_label.grid(row=9, column=0, columnspan=1, sticky="w")
        self.triggercbb.grid(row=9, column=2, columnspan=3)
        self.publish_button.grid(row=10, columnspan=6, pady=10)

        # Add input panels to window
        self.input_upper.pack(side="top", fill="both", expand=True)
        self.input_lower.pack(side="top", fill="both", expand=True)

        # Output pane (right)
        self.title_frame = tk.Frame(self)

        self.titlelabel = tk.Label(
            self.title_frame, text="Output:", font=('', 11, 'bold'))
        self.titlelabel.pack()

        self.output = tk.Listbox(self, selectmode=tk.SINGLE)
        self.output.config(width=100, height=100)
        self.output.grid(row=1, column=1)

        # # Status bar
        self.status_frame = tk.Frame(self)
        self.status = tk.Label(
            self.status_frame, text="Ready...", relief=tk.SUNKEN, anchor='w')
        self.status.pack(fill="both", expand=True)

        # Add output pane and status bar to parent
        self.input.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.title_frame.grid(row=0, column=1, sticky="ew")
        self.output.grid(row=1, column=1, sticky="nsew")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)


if __name__ == "__main__":
    window = tk.Tk()
    window.minsize(1080, 640)
    window.maxsize(1080, 640)
    window.title(
        "Publish & Audit Trade Signals on the Ethereum Blockchain")
    App(window).pack(side="top", fill="both", expand=True)
    window.mainloop()

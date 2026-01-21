from ib_insync import IB

ib = IB()
ib.connect(
    host='127.0.0.1',
    port=4002,      # Paper
    clientId=1
)

print("Connected:", ib.isConnected())
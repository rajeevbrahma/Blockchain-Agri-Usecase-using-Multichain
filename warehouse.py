
import Savoir
import logging
from MultichainPython import Multichainpython
import simplejson as json
from pubnub import Pubnub

LOG_FILENAME = 'retailstore.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


'''SYSTEM 2 PROGRAM'''
class Warehouse:
        def __init__(self,rpcuser,rpcpasswd,rpchost,rpcport,chainname):
                print "Warehouse"
                # self.mchain = Multichainpython(rpcuser,rpcpasswd,rpchost,rpcport,chainname)
                self.rpcuser = rpcuser
                self.rpcpasswd = rpcpasswd
                self.rpchost = rpchost
                self.rpcport = rpcport
                self.chainname = chainname
                self.mchain = Multichainpython(self.rpcuser,self.rpcpasswd,self.rpchost,self.rpcport,self.chainname)

        def connectTochain(self):       
                return self.mchain.multichainConnect()
        def warehouseAddress(self):
                return self.mchain.accountAddress()

        def assetsubscribe(self,asset):
                self.mchain.subscribeToasset(asset)

        def queryassettranx(self,asset):        
                print self.mchain.queryAssetTransactions(asset)

        def queryasstdetails(self,asset):       
                print self.mchain.queryassetsdetails(asset) 

         def issueWHasset(self): 
                try:
                        assetaddress = self.mchain.accountAddress()
                        assetname = "money1" 
                        assetdetails = {"name":assetname,"open":True} # along withthat a unique timestamp will be added
                        assetquantity = 100 # may be a fixed or random number generated by a logic
                        assetunit = 1# This also a random generated based on logic still not clear 
                        assetnativeamount =0 # not clear
                        assetcustomfield = {'currency':'dollars','owner':'John'}# will be generated based on sensor data, fields will be decided$
                        self.assetsubscribe(assetname)
                        issueWHasset_return = self.mchain.issueAsset(assetaddress,assetdetails,assetquantity,assetunit,assetnativeamount,assetcustomfield)
                        publish_handler({"messagetype":"resp","message":issueWHasset_return})
                except Exception as e:
                        print e,"error in issueHWasset"
        def issuemoreFarmasset(self,assetname,assetcustomfield):
                assetaddress = self.mchain.accountAddress()
                issuemoreFarmasset_return = self.mchain.issueMoreAsset(assetaddress,assetname,assetcuctomfield)
                publish_handler({"messagetype":"resp","message":issuemoreFarmasset_return})

        def createExchange(self,ownasset,otherasset):
                try:
                        # Here asset will be a dictionary ex: {"asset1":1}
                        prepare_return = self.mchain.preparelockunspentexchange(ownasset)
                        if prepare_return != False:
                                createex_return = self.mchain.createExchange(prepare_return["txid"],prepare_return["vout"],otherasset)
                                print createex_return
                                publish_handler({"messagetype":"resp","hexblob":createex_return})
                        else:
                                publish_handler({"messagetype":"resp","hexblob":""})    
                except Exception as e:
                        print e,"error in createExchange"       


        def decodeExchange(self,hexBlob,ownasset,otherasset):
                # The following will give the details regarding the exchange 
                # --step3
                print self.mchain.decoderawExchange(hexBlob)
                # --step4
                # here asset will be the farmer's asset
                prepare_return = self.mchain.preparelockunspentexchange(ownasset)
                print prepare_return
                # --step5 
                # This return value will contain a field called "complete"
                # if it is set to True, the transaction happend successfully
                append_return = self.mchain.appendrawExchange(hexBlob,prepare_return["txid"],prepare_return["vout"],otherasset)
                print append_return
                # -- step 6 
                # This step is for sending the transaction details to the chain
                if append_return["complete"] == True:
                        send_return = self.mchain.sendrawTransaction(append_return["hex"])
        
                
def pub_Init(): 
        global pubnub
        try:
                pubnub = Pubnub(publish_key=pub_key,subscribe_key=sub_key) 
                pubnub.subscribe(channels='warehouse', callback=callback,error=error,
                connect=connect, reconnect=reconnect, disconnect=disconnect)    
                return True
        except Exception as pubException:
                logging.error("The pubException is %s %s"%(pubException,type(pubException)))
                return False    

                        

def callback(message,channel):
        try:
                print message
                if message["messagetype"] == "req":
                        if message["messagecode"] == "issueasset":
                                WH.issueWHasset()
                        if message["messagecode"] == "createexchange":
                                WH.issueWHasset()
                        if message["messagecode"] == "createexchange":
                                WH.createExchange(message["ownasset"],message["otherasset"])
                        if message["messagecode"] == "decodeexchange":
                                WH.decodeExchange(message["hexblob"],message["ownasset"],message["otherasset"]) 
                        if message["messagecode"] == "assettranx":
                                WH.queryassettranx(message["asset"])
                        if message["messagecode"] == "assetdetails":
                                WH.queryasstdetails(message["asset"])
                        
        except Exception as e:
                print e,"callback error"
                #logging.error("The callback exception is %s,%s"%(e,type(e)))           
                #logging.info(message)


def publish_handler(message):

        try:
                pbreturn = pubnub.publish(channel = channel ,message = message,error=error)

        except Exception as error_pbhandler:
                print error_pbhandler

                
def error(message):
        logging.error("ERROR on Pubnub: " + str(message))

def connect(message):
        logging.info("CONNECTED")

def reconnect(message):
    logging.info("RECONNECTED")

def disconnect(message):
     logging.info("DISCONNECTED")
                
if __name__ == '__main__':
        channel = 'UI'
        pubnub = None   
        # PUBNUB KEYS
        pub_key = 'pub-c-abde89c6-da51-4c04-8c2b-9c3984e1182d'
        sub_key = 'sub-c-d17a927c-e171-11e6-802a-02ee2ddab7fe'
        pub_Init()
        rpcuser='multichainrpc'
        rpcpasswd='CnkG5ezKnKvVVNPvTatoZsC2ZSteLdSQL84ZzAgqwe1u'
        rpchost = 'localhost'
        rpcport = '6296'
        chainname = 'chain1'
        WH = Warehouse(rpcuser,rpcpasswd,rpchost,rpcport,chainname)
        print WH.connectTochain()
        print WH.warehouseAddress()

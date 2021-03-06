import os
import sys
import Savoir
import logging
import simplejson as json
from pubnub import Pubnub

parentpath = os.path.dirname(os.getcwd())
sys.path.insert(0,parentpath)
from MultichainPython import Multichainpython
from fileparser import ConfigFileParser


LOG_FILENAME = 'farmland.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Farmland:
	def __init__(self,rpcuser,rpcpasswd,rpchost,rpcport,chainname):
		print "Farmland"
		self.rpcuser = rpcuser
		self.rpcpasswd = rpcpasswd
		self.rpchost = rpchost
		self.rpcport = rpcport
		self.chainname = chainname
		self.mchain = Multichainpython(self.rpcuser,self.rpcpasswd,self.rpchost,self.rpcport,self.chainname)

	def connectTochain(self):
		return self.mchain.multichainConnect()  
	def farmAddress(self):
		return self.mchain.accountAddress()
	def assetbalances(self):
		print self.mchain.gettotalbalances()	

	def assetsubscribe(self,asset):
		self.mchain.subscribeToasset(asset)

	def queryassettranx(self,asset):
		print self.mchain.queryAssetTransactions(asset)

	def queryasstdetails(self,asset):
		print self.mchain.queryassetsdetails(asset)     
	def issueFSasset(self): 
		try:
		    assetaddress = self.mchain.accountAddress()
		    assetname = "crop"
		    assetdetails = {"name":assetname,"open":True} # along w$
		    assetquantity = 100 # may be a fixed or random number g$
		    assetunit = 1 # This also a random generated based on lo$
		    assetnativeamount =0 # not clear
		    assetcustomfield ={"assetmetrics":"kgs",'croptemp':'27','crophumidity':'10','startdate':'2017-03-01','enddate':'2017-04-30',"asset-departuredate":'2017-05-05','farmer':'Mark-Farmer'}
		    issueFSasset_return = self.mchain.issueAsset(assetaddress,assetdetails,assetquantity,assetunit,assetnativeamount,assetcustomfield)

		    self.assetsubscribe(assetname)
		    
		    assetdescription = {"assetname":assetname,"assetquantity":assetquantity,"assetmetrics":"kgs"}
		    message = {"op-return":issueFSasset_return,"assetdescription":assetdescription}

		    publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})
		except Exception as e:
		    print e,"erro in issueFSasset"
		    message = {"op-return":"error","message":e}
		    publish_handler({"messagecode":"issueasset","messagetype":"resp","message":message})



	
	def createExchange(self,ownasset,otherasset):
		try:
			# Here asset will be a dictionary ex: {"asset1":1}
			prepare_return = self.mchain.preparelockunspentexchange(ownasset)
			print prepare_return
			if prepare_return != False:
				createex_return = self.mchain.createrawExchange(prepare_return["txid"],prepare_return["vout"],otherasset)
				print createex_return
				message = {"op-return":createex_return,"hexblob":str(hexblob)}
				publish_handler({"messagecode":"createexchange","messagetype":"resp","hexblob":message})
			else:
				publish_handler({"messagecode":"createexchange","messagetype":"resp","hexblob":""})   
		except Exception as e:
				print e,"error in createExchange"
				publish_handler({"messagecode":"createexchange","messagetype":"resp","hexblob":""})       
		
def pub_Init(): 
	global pubnub
	try:
	    pubnub = Pubnub(publish_key=pub_key,subscribe_key=sub_key) 
	    pubnub.subscribe(channels=subchannel, callback=callback,error=error,
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
		            FL.issueFSasset()
		    if message["messagecode"] == "issuemoreasset":
		            FL.issueFSasset(message["asset"],message["assetcustomfield"])
		    if message["messagecode"] == "createexchange":
		            FL.createExchange(message["ownasset"],message["otherasset"])		            
		    if message["messagecode"] == "assettranx":
		            FL.queryassettranx(message["asset"])
		    if message["messagecode"] == "assetdetails":
		            FL.queryasstdetails(message["asset"])
  			if message["messagecode"] == "assetbalance":
                    FL.assetbalances()

	except Exception as e:
	    logging.error("The callback exception is %s,%s"%(e,type(e)))            
	    logging.info(message)


def publish_handler(message):
	try:
	    pbreturn = pubnub.publish(channel = pubchannel ,message = message,error=error)

	except Exception as error_pdhandler:
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
	pubnub = None
	filename = "config.ini"
	cf = ConfigFileParser()		
	cf.parseConfig(filename)

	# PUBNUB KEYS
	pub_key = cf.getConfig("pubkey")
	sub_key = cf.getConfig("subkey")  

	pubchannel = cf.getConfig("pubchannel")
	subchannel = cf.getConfig("subchannel")

	# Multichain  Credentials
	rpcuser= cf.getConfig("rpcuser")
	rpcpasswd=cf.getConfig("rpcpasswd")
	rpchost = cf.getConfig("rpchost")
	rpcport = cf.getConfig("rpcport")
	chainname = cf.getConfig("chainname")

	FL = Farmland(rpcuser,rpcpasswd,rpchost,rpcport,chainname)
	FL.connectTochain()
	pub_Init()





# def issuemoreFarmasset(self,assetname,assetcustomfield):
	# 	try:
	# 		assetaddress = self.mchain.accountAddress()
	# 		issuemorefarmasset_return = self.mchain.issueMoreAsset(assetaddress,assetname,assetcuctomfield)
			
	# 		assetdescription = {"assetname":assetname,"assetcustomfield":assetcustomfield}
	# 	    message = {"op-return":issuemorefarmasset_return,"assetdescription":assetdescription}
	# 		publish_handler({"messagecode":"issuemoreasset","messagetype":"resp","message":message})
		
	# 	except Exception as e:
	# 		print e,"issuemoreasset error"
	# 		message = {"op-return":"error","message":e}
	# 	    publish_handler({"messagecode":"issuemoreasset","messagetype":"resp","message":message})




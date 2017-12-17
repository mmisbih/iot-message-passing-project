from abc import ABC, abstractmethod

class IClient(ABC):
    @abstractmethod
    def connect(self):
        raise NotImplementedError( "Should have implemented this" )

    @abstractmethod
    def publish(self):
        raise NotImplementedError( "Should have implemented this" )

    @abstractmethod
    def subscribe(self):
        raise NotImplementedError( "Should have implemented this" )

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError( "Should have implemented this" )
        
    @abstractmethod
    def waitForClient(self):
        raise NotImplementedError( "Should have implemented this" )
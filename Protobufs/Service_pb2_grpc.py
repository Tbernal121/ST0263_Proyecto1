# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import Service_pb2 as Service__pb2


class NameNodeServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.LeaderHeartbeat = channel.unary_unary(
                '/NameNodeService/LeaderHeartbeat',
                request_serializer=Service__pb2.NameNodeInfo.SerializeToString,
                response_deserializer=Service__pb2.LeaderInfo.FromString,
                )
        self.ListFiles = channel.unary_unary(
                '/NameNodeService/ListFiles',
                request_serializer=Service__pb2.Empty.SerializeToString,
                response_deserializer=Service__pb2.FileList.FromString,
                )
        self.CreateFile = channel.unary_unary(
                '/NameNodeService/CreateFile',
                request_serializer=Service__pb2.FileInfo.SerializeToString,
                response_deserializer=Service__pb2.DataNodeIDS.FromString,
                )
        self.GetBlockLocations = channel.unary_unary(
                '/NameNodeService/GetBlockLocations',
                request_serializer=Service__pb2.FileName.SerializeToString,
                response_deserializer=Service__pb2.BlockLocations.FromString,
                )
        self.UpdateFileBlocks = channel.unary_unary(
                '/NameNodeService/UpdateFileBlocks',
                request_serializer=Service__pb2.FileInfo.SerializeToString,
                response_deserializer=Service__pb2.Status.FromString,
                )
        self.RelocateBlocks = channel.unary_unary(
                '/NameNodeService/RelocateBlocks',
                request_serializer=Service__pb2.BlockRelocation.SerializeToString,
                response_deserializer=Service__pb2.Status.FromString,
                )


class NameNodeServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def LeaderHeartbeat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListFiles(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetBlockLocations(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateFileBlocks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RelocateBlocks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NameNodeServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'LeaderHeartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.LeaderHeartbeat,
                    request_deserializer=Service__pb2.NameNodeInfo.FromString,
                    response_serializer=Service__pb2.LeaderInfo.SerializeToString,
            ),
            'ListFiles': grpc.unary_unary_rpc_method_handler(
                    servicer.ListFiles,
                    request_deserializer=Service__pb2.Empty.FromString,
                    response_serializer=Service__pb2.FileList.SerializeToString,
            ),
            'CreateFile': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateFile,
                    request_deserializer=Service__pb2.FileInfo.FromString,
                    response_serializer=Service__pb2.DataNodeIDS.SerializeToString,
            ),
            'GetBlockLocations': grpc.unary_unary_rpc_method_handler(
                    servicer.GetBlockLocations,
                    request_deserializer=Service__pb2.FileName.FromString,
                    response_serializer=Service__pb2.BlockLocations.SerializeToString,
            ),
            'UpdateFileBlocks': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateFileBlocks,
                    request_deserializer=Service__pb2.FileInfo.FromString,
                    response_serializer=Service__pb2.Status.SerializeToString,
            ),
            'RelocateBlocks': grpc.unary_unary_rpc_method_handler(
                    servicer.RelocateBlocks,
                    request_deserializer=Service__pb2.BlockRelocation.FromString,
                    response_serializer=Service__pb2.Status.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'NameNodeService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NameNodeService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def LeaderHeartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NameNodeService/LeaderHeartbeat',
            Service__pb2.NameNodeInfo.SerializeToString,
            Service__pb2.LeaderInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListFiles(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NameNodeService/ListFiles',
            Service__pb2.Empty.SerializeToString,
            Service__pb2.FileList.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NameNodeService/CreateFile',
            Service__pb2.FileInfo.SerializeToString,
            Service__pb2.DataNodeIDS.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetBlockLocations(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NameNodeService/GetBlockLocations',
            Service__pb2.FileName.SerializeToString,
            Service__pb2.BlockLocations.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateFileBlocks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NameNodeService/UpdateFileBlocks',
            Service__pb2.FileInfo.SerializeToString,
            Service__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RelocateBlocks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/NameNodeService/RelocateBlocks',
            Service__pb2.BlockRelocation.SerializeToString,
            Service__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class DataNodeServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendHeartbeat = channel.unary_unary(
                '/DataNodeService/SendHeartbeat',
                request_serializer=Service__pb2.DataNodeID.SerializeToString,
                response_deserializer=Service__pb2.Status.FromString,
                )
        self.InitialContact = channel.unary_unary(
                '/DataNodeService/InitialContact',
                request_serializer=Service__pb2.DataNodeID.SerializeToString,
                response_deserializer=Service__pb2.Status.FromString,
                )
        self.StoreBlock = channel.unary_unary(
                '/DataNodeService/StoreBlock',
                request_serializer=Service__pb2.BlockData.SerializeToString,
                response_deserializer=Service__pb2.Status.FromString,
                )
        self.DeleteBlock = channel.unary_unary(
                '/DataNodeService/DeleteBlock',
                request_serializer=Service__pb2.BlockId.SerializeToString,
                response_deserializer=Service__pb2.Status.FromString,
                )
        self.SendBlock = channel.unary_unary(
                '/DataNodeService/SendBlock',
                request_serializer=Service__pb2.BlockId.SerializeToString,
                response_deserializer=Service__pb2.BlockData.FromString,
                )


class DataNodeServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendHeartbeat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def InitialContact(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StoreBlock(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteBlock(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendBlock(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DataNodeServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendHeartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.SendHeartbeat,
                    request_deserializer=Service__pb2.DataNodeID.FromString,
                    response_serializer=Service__pb2.Status.SerializeToString,
            ),
            'InitialContact': grpc.unary_unary_rpc_method_handler(
                    servicer.InitialContact,
                    request_deserializer=Service__pb2.DataNodeID.FromString,
                    response_serializer=Service__pb2.Status.SerializeToString,
            ),
            'StoreBlock': grpc.unary_unary_rpc_method_handler(
                    servicer.StoreBlock,
                    request_deserializer=Service__pb2.BlockData.FromString,
                    response_serializer=Service__pb2.Status.SerializeToString,
            ),
            'DeleteBlock': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteBlock,
                    request_deserializer=Service__pb2.BlockId.FromString,
                    response_serializer=Service__pb2.Status.SerializeToString,
            ),
            'SendBlock': grpc.unary_unary_rpc_method_handler(
                    servicer.SendBlock,
                    request_deserializer=Service__pb2.BlockId.FromString,
                    response_serializer=Service__pb2.BlockData.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'DataNodeService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class DataNodeService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendHeartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/DataNodeService/SendHeartbeat',
            Service__pb2.DataNodeID.SerializeToString,
            Service__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def InitialContact(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/DataNodeService/InitialContact',
            Service__pb2.DataNodeID.SerializeToString,
            Service__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def StoreBlock(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/DataNodeService/StoreBlock',
            Service__pb2.BlockData.SerializeToString,
            Service__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteBlock(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/DataNodeService/DeleteBlock',
            Service__pb2.BlockId.SerializeToString,
            Service__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendBlock(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/DataNodeService/SendBlock',
            Service__pb2.BlockId.SerializeToString,
            Service__pb2.BlockData.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

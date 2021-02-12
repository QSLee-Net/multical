from multical import tables
from structs.struct import struct, subset
from multical.optimization.parameters import Parameters
from cached_property import cached_property
from multical.io.export import export_poses

from multical.transform import rtvec
from .parameters import IndexMapper

class PoseSet(Parameters):
  def __init__(self, pose_table, names=None):
    self.pose_table = pose_table
    self.names = names or [str(i) for i in range(self.size)]

  @property
  def size(self):
    return self.poses.shape[0]

  @cached_property
  def valid(self):
    return self.pose_table.valid

  @cached_property
  def inverse(self):
    return self.copy(pose_table=tables.inverse(self.pose_table))

  @cached_property
  def poses(self):
    return self.pose_table.poses

  @cached_property
  def params(self):
    return rtvec.from_matrix(self.poses).ravel()

  def with_params(self, params):
    m = rtvec.to_matrix(params.reshape(-1, 6))
    return self.copy(pose_table = self.pose_table._update(poses=m))

  def sparsity(self, index_mapper : IndexMapper, axis : int):
    return index_mapper.pose_mapping(self.pose_table, axis=axis)

  def export(self):
    return struct(poses = export_poses(self.pose_table, self.names))

  def __getstate__(self):
    attrs = ['pose_table', 'names']
    return subset(self.__dict__, attrs)

  def copy(self, **k):
    """Copy object and change some attribute (no mutation)"""
    d = self.__getstate__()
    d.update(k)
    return self.__class__(**d)
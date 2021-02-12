from cached_property import cached_property
from structs.struct import struct, subset
from .motion_model import MotionModel

from multical.optimization.parameters import IndexMapper, Parameters
from multical import tables

from multical.transform import rtvec

class RollingFrames(MotionModel, Parameters):

  def __init__(self, pose_start, pose_end, valid, names):
    self.pose_start = pose_start
    self.pose_end = pose_end
    self.valid = valid
    self.names = names

  @property
  def size(self):
    return self.poses.shape[0]

  @cached_property
  def valid(self):
    return self.pose_table.valid

  @staticmethod
  def init(pose_table, names=None):
    size = pose_table.valid.size
    names = names or [str(i) for i in range(size)]


  @cached_property
  def params(self):
    return [
      rtvec.from_matrix(self.pose_start).ravel(),
      rtvec.from_matrix(self.pose_end).ravel()
    ]
      

  def with_params(self, params):
    m = rtvec.to_matrix(params.reshape(-1, 6))
    return self.copy(pose_table = self.pose_table._update(poses=m))

  def sparsity(self, index_mapper : IndexMapper, axis : int):
    return index_mapper.pose_mapping(self.pose_table, axis=axis)

  def export(self):
    return {i:struct(start=start.poses.tolist(), end=end.poses.tolist()) 
      for i, start, end, valid in zip(self.names, self.pose_start, self.pose_end, self.valid) 
        if valid}

  def __getstate__(self):
    attrs = ['pose_start', 'pose_end', 'valid']
    return subset(self.__dict__, attrs)

  def copy(self, **k):
    """Copy object and change some attribute (no mutation)"""
    d = self.__getstate__()
    d.update(k)
    return self.__class__(**d)
  
  
  # @cached_property
  # def times(self):
  #   image_heights = np.array([camera.image_size[1] for camera in self.cameras])    
  #   return self.point_table.points[..., 1] / np.expand_dims(image_heights, (1,2,3))

  # @cached_property
  # def transformed_rolling(self):
  #   poses = self.pose_estimates
  #   start_frame = np.expand_dims(poses.rig.poses, (0, 2, 3))
  #   end_frame = np.expand_dims(self.frame_motion.poses, (0, 2, 3))
    
  #   frame_poses = interpolate_poses(start_frame, end_frame, self.times)
  #   view_poses = np.expand_dims(poses.camera.poses, (1, 2, 3)) @ frame_poses  

  #   board_points = self.stacked_boards
  #   board_points_t = matrix.transform_homog(t = np.expand_dims(poses.board.poses, 1), points = board_points.points)

  #   return struct(
  #     points = matrix.transform_homog(t = view_poses, points = np.expand_dims(board_points_t, (0, 1))),
  #     valid = self.valid
  #   )

 
  #  @cached_property
  # def transformed_rolling_linear(self):
  #   poses_start = self.pose_estimates
  #   poses_end = poses_start._extend(rig=self.frame_motion)

  #   table_start = tables.expand_poses(poses_start)
  #   table_end = tables.expand_poses(poses_end)

  #   start_frame = transform_points(table_start, self.stacked_boards)
  #   end_frame = transform_points(table_end, self.stacked_boards)

  #   return struct(
  #     points = lerp(start_frame.points, end_frame.points, self.times),
  #     valid = start_frame.valid & end_frame.valid
  #   )
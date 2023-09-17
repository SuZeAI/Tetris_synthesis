from keras.callbacks import TensorBoard
from torch.utils.tensorboard import FileWriter

class CustomTensorBoard(TensorBoard):
    def __init__(self, **kwargs):
        super(CustomTensorBoard, self).__init__(**kwargs)
        self.writer = FileWriter(self.log_dir)

    def set_model(self, model):
        pass

    def log(self, step, **stats):
        self._write_logs(stats, step)

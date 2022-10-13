"""
"""
import glob
import os

from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms
from tqdm import tqdm


class PraTodosVerem(Dataset):
    """
    #PraTodosVerem Dataset.

    Dataset inspirado nas implementações dos datasets do torchvision.
    Alguns exemplos:
    https://pytorch.org/vision/stable/_modules/torchvision/datasets/cifar.html#CIFAR10
    https://pytorch.org/vision/stable/_modules/torchvision/datasets/coco.html#CocoCaptions

    Examples
    --------
    import pra_todos_verem.datasets as datasets
    ptv = datasets.PraTodosVerem(root='data/raw/posts/')

    print('Number of samples: ', len(ptv))
    img, target = ptv[3] # load 4th sample

    print("Image Size: ", img.size())
    print(target)
    """

    def __init__(
        self,
        root: str = "data/raw/posts/",
    ):
        """
        #PraTodosVerem dataset.

        Parameters
        ----------
        root : str
            Diretório raiz do dataset #PraTodosVerem.
        """
        self.root = root

        self.ids = []
        self.load_ids()

    def __len__(self) -> int:
        return len(self.ids)

    def __getitem__(self, index: int):
        id_ = self.ids[index]
        image = self.load_image(id_)
        target = self.load_target(id_)

        img = self.to_tensor(image)

        return img, target

    def to_tensor(self, image):
        return transforms.ToTensor()(image).unsqueeze_(0)

    def load_ids(self):
        """
        Iterates through .jpg and .png files in self.root and saves their ids.
        """
        for filepath in tqdm(glob.iglob(f"{self.root}**/*.*", recursive=True)):
            dirname, filename = os.path.split(filepath[:-4])
            _, ext = os.path.splitext(filename)

            if ext in {".jpg", ".png"}:
                id_ = f"{os.path.basename(dirname)}_{filename}"
                self.ids.append(id_)

    def load_image(self, id: str):
        """
        Loads an image into a Tensor object.

        Parameters
        ----------
        id : str

        Returns
        -------
        torch.Tensor
        """
        filepath = id.replace("_", "/")
        return Image.open(os.path.join(self.root, filepath)).convert("RGB")

    def load_target(self, id: str) -> str:
        """
        Loads the description text.

        Parameters
        ----------
        id : str

        Returns
        -------
        str
        """
        return open(os.path.join(self.root, id.split("_")[0], "caption.txt"), "r").read()

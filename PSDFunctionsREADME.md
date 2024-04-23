Common Python functions which can help in DocumentAutomation

---------------------------------------------------------------------------------------------
shake_image will shuffle the original image contents. You should give the JSON output of
the original image obtained from the DA and the image apart from the X/Y coordinates.
if __name__ == "__main__":
      psd.shake_image('sample-invoice.jpg','sample-invoice.json',100, 500, 20, 200, 10)
---------------------------------------------------------------------------------------------
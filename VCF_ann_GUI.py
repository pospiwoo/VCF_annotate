import os, Tkinter, tkFileDialog
import VCF_ann as VCF
from os.path import dirname, abspath

class VCF_ann_GUI(Tkinter.Frame):
    def __init__(self, root):
	self.dir = dirname(abspath(__file__))
        Tkinter.Frame.__init__(self, root)
	self.VCF_file = ""
        self.output_file_name = ""

	# define buttons
	button_row_ind = 0
	Tkinter.Label(self, text="Select VCF file").grid(row=button_row_ind,column=0)
	Tkinter.Button(self, text="Select VCF file", command=self.ask_VCF_filename).grid(row=button_row_ind,column=1)

	button_row_ind += 1
	Tkinter.Label(self, text="Output file name").grid(row=button_row_ind,column=0)
	self.output_file_name = Tkinter.StringVar()
	Tkinter.Entry(self, textvariable=self.output_file_name).grid(row=button_row_ind,column=1)

	button_row_ind += 1
	Tkinter.Button(self, text ="Run", command = self.submit).grid(row=button_row_ind,column=0)

    def ask_VCF_filename(self):
        self.VCF_file = tkFileDialog.askopenfilename(title="Select VCF file", initialdir=self.dir)
        Tkinter.Label(self, text=os.path.basename(self.VCF_file)).grid(row=0,column=2)

    def submit(self):
        self.output_file_name = os.path.join(self.dir, str(self.output_file_name.get()))
	# init instance and run driver functions
	annVCF_obj = VCF.annotateVCF(self.VCF_file, self.output_file_name)
	annVCF_obj.process()
	# change to exit button when done
	Tkinter.Button(self, text ="Done(exit)", command = self.exit_call).grid(row=2,column=0)

    def exit_call(self):
	exit()


if __name__=="__main__":
    root = Tkinter.Tk()
    VCF_ann_GUI(root).pack()
    root.wm_title("GUI for VCF_ann")
    root.mainloop()


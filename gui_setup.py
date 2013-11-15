import os
import os.path
import sys
import Tkinter
import ttk
import tkFileDialog as filedialog
import tkMessageBox
from Tkconstants import *
from Bio import SeqIO as so
from vertical_scroll import VerticalScrolledFrame as vsf
from output_tabs_checkboxes import all_checkboxes_dict
from multiprocessing import cpu_count
from gui_execute import execute


class pyigblast_gui():

    '''gui class, will do everything including calling on executables'''

    def __init__(self, root):
        # Initialization
        self.root = root
        _program_name = sys.argv[0]
        self._directory_name = os.path.dirname(os.path.abspath(_program_name))
        self._user_directory = os.path.expanduser("~")
        # argument dictionary we will pass to the arg parser eventually
        self.output_entry = ""
        self.argument_dict = {
            'query': '',
            'database': self._directory_name + "/database/",
            'in_data': self._directory_name + "/internal_data/",
            'aux_data': self._directory_name + "/optional_file/",
            'output_file': self._user_directory + "/pyigblast_output",
            'tmp_data': self._user_directory + "/pyigblast_temporary/"}
        window_info = self.root.winfo_toplevel()
        window_info.wm_title('PyIgBLAST - GUI')
        window_info.geometry('2200x1500+10+10')
        # creates main menu
        self.MainMenu()
        # creates main menu notebook inside
        self.TabNotebook()

    def MainMenu(self):
        main_menu = ttk.Frame(self.root)
        author_label = ttk.Label(main_menu, text="Jordan Willis")
        university_label = ttk.Label(main_menu, text="Vanderbilt University")
        exit_button = ttk.Button(
            main_menu, text="Exit",
            command=lambda root=self.root: root.destroy())
        refresh_button = ttk.Button(
            main_menu, text="Refresh", command=lambda self=self: self._update())
        run_button = ttk.Button(
            main_menu, text="Run", command=lambda self=self: self.execute())
        author_label.pack(side=LEFT, fill=X, padx=10, pady=10)
        run_button.pack(side=LEFT, expand=1, fill=X, padx=10, pady=10)
        refresh_button.pack(side=LEFT, expand=1, fill=X, padx=10, pady=10)
        exit_button.pack(side=LEFT, expand=1, fill=X, padx=10, pady=10)
        university_label.pack(side=RIGHT, fill=X, padx=10, pady=10)
        main_menu.pack(side=BOTTOM, fill=X, pady=10)

    def TabNotebook(self):
        main_notebook_frame = ttk.Notebook(self.root, name='main_notebook')
        main_notebook_frame.enable_traversal()
        main_notebook_frame.pack(side=TOP, expand=1, fill=BOTH)
        self._create_files_and_directories(main_notebook_frame)
        self._create_format_output(main_notebook_frame)
        self._create_readme(main_notebook_frame)

    def _create_files_and_directories(self, notebook_frame):
        # This is the first tab that houses files, directories and Options
        # First frame in the notebook
        f_and_d_frame = ttk.Frame(notebook_frame, name='f_and_d')
        fasta_input_frame = ttk.LabelFrame(f_and_d_frame)
        fasta_input_frame.pack(side=TOP, expand=0, fill=X, padx=10)
        # put in fasta_entry frame to take in input
        self._make_fasta_entry(fasta_input_frame)

        # Set up directory frame within the tab that takes in all the
        # directories needed to run run blast
        directories_frame = ttk.LabelFrame(f_and_d_frame)
        directories_frame.pack(side=LEFT, expand=1, fill=BOTH)
        directory_label = ttk.Label(directories_frame, font=('Arial', 20),
                                    text="Directories needed to run blast:")
        directory_label.pack(side=TOP, fill=X, padx=20, pady=10)

        # set now run functions to place directories within that frame
        self._set_up_directories(directories_frame)

        # On the other side of this tab we will put in the basic options
        # including output type and blast
        basic_options_frame = ttk.LabelFrame(f_and_d_frame)
        basic_options_frame.pack(side=LEFT, fill=BOTH, padx=5)
        self._set_up_basic_options(basic_options_frame)

        # and add it to the big frame
        notebook_frame.add(
            f_and_d_frame, text="Input Options", underline=0, padding=2)

    def _make_fasta_entry(self, fasta_input_frame):
        message = ttk.Label(
            fasta_input_frame, relief=FLAT, width=500, anchor=W,
            text='Enter the entry FASTA file here', font=('Arial', 20))
        fasta_entry = ttk.Entry(fasta_input_frame, width=10)
        fasta_entry_button = ttk.Button(fasta_input_frame, text="Browse...",
                                        command=lambda entry=fasta_entry: self._enter_fasta(entry))
        message.pack(side=TOP, expand=1, fill=BOTH, padx=3, pady=3)
        fasta_entry.pack(side=LEFT, padx=3, expand=1, fill=X, pady=3)
        fasta_entry_button.pack(side=LEFT, fill=X)

    def _enter_fasta(self, entry):
        fn = None
        _not_fasta = True
        opts = {'title': "Select FASTA file to open...",
                'initialfile': entry.get()}
        while _not_fasta:
            fn = filedialog.askopenfilename(**opts)
            try:
                so.parse(str(fn), 'fasta').next()
                _not_fasta = False
                if fn:
                    entry.delete(0, END)
                    entry.insert(END, fn)
                    self.argument_dict['query'] = str(fn)
            except StopIteration:
                tkMessageBox.showwarning(
                    "Open file",
                    "Cannot open {0}, it is not a FASTA file\n".format(fn))

    def _set_up_directories(self, directories_frame):
        # blast directory
        blast_directories_frame = ttk.LabelFrame(directories_frame)
        blast_directories_frame.pack(side=TOP, fill=X, padx=10, expand=1)
        blast_directories_label = ttk.Label(
            blast_directories_frame, text="Compiled Blast Directory:", font=('Arial', 16))
        blast_directories_label.pack(side=TOP, anchor=NW)
        blast_directory_entry = ttk.Entry(blast_directories_frame)
        blast_directory_entry.insert(END, self.argument_dict['database'])
        blast_directory_entry.pack(side=LEFT, expand=1, fill=X, pady=3)
        blast_directory_button = ttk.Button(
            blast_directories_frame, text="Browse...",
            command=lambda type='blast', entry=blast_directory_entry: self._enter_directory(type, entry))
        blast_directory_button.pack(side=LEFT, fill=X)

        # internal_blast directory
        internal_blast_directories_frame = ttk.LabelFrame(directories_frame)
        internal_blast_directories_frame.pack(
            side=TOP, fill=X, padx=10, expand=1)
        internal_blast_directories_label = ttk.Label(
            internal_blast_directories_frame, text="Internal Blast Directory:", font=('Arial', 16))
        internal_blast_directories_label.pack(side=TOP, anchor=NW)
        internal_blast_directory_entry = ttk.Entry(
            internal_blast_directories_frame)
        internal_blast_directory_entry.insert(
            END, self.argument_dict['in_data'])
        internal_blast_directory_entry.pack(
            side=LEFT, expand=1, fill=X, pady=3)
        internal_blast_directory_button = ttk.Button(
            internal_blast_directories_frame, text="Browse...",
            command=lambda type='in_data', entry=internal_blast_directory_entry: self._enter_directory(type, entry))
        internal_blast_directory_button.pack(side=LEFT, fill=X)

        # auxilliary_blast directory
        aux_blast_directories_frame = ttk.LabelFrame(directories_frame)
        aux_blast_directories_frame.pack(side=TOP, fill=X, padx=10, expand=1)
        aux_blast_directories_label = ttk.Label(
            aux_blast_directories_frame, text="Auxillary Blast Directory:", font=('Arial', 16))
        aux_blast_directories_label.pack(side=TOP, anchor=NW)
        aux_blast_directory_entry = ttk.Entry(
            aux_blast_directories_frame)
        aux_blast_directory_entry.insert(END, self.argument_dict['aux_data'])
        aux_blast_directory_entry.pack(side=LEFT, expand=1, fill=X, pady=3)
        aux_blast_directory_button = ttk.Button(
            aux_blast_directories_frame, text="Browse...",
            command=lambda type='aux_data', entry=aux_blast_directory_entry: self._enter_directory(type, entry))
        aux_blast_directory_button.pack(side=LEFT, fill=X)

        # auxilliary_blast directory
        tmp_directories_frame = ttk.LabelFrame(directories_frame)
        tmp_directories_frame.pack(side=TOP, fill=X, padx=10, expand=1)
        tmp_directories_label = ttk.Label(
            tmp_directories_frame, text="Directory to store temporary files in:",
            font=('Arial', 16))
        tmp_directories_label.pack(side=TOP, anchor=NW)
        tmp_directory_entry = ttk.Entry(tmp_directories_frame)
        tmp_directory_entry.insert(END, self.argument_dict['tmp_data'])
        tmp_directory_entry.pack(side=LEFT, expand=1, fill=X, pady=3)
        tmp_directory_button = ttk.Button(
            tmp_directories_frame, text="Browse...",
            command=lambda type='tmp_data', entry=tmp_directory_entry: self._enter_directory(type, entry))
        tmp_directory_button.pack(side=LEFT, fill=X)

    def _enter_directory(self, type, entry):
        direc = None
        tkMessageBox.showinfo(
            "Consult:", "Please Read the README tab before messing with this option")
        opts = {'title': "Select FASTA file to open...",
                'initialdir': entry.get()}
        direc = filedialog.askdirectory(**opts)
        if direc:
            entry.delete(0, END)
            entry.insert(END, fn)
            if type == 'blast':
                self.argument_dict['database'] = str(direc)
            elif type == 'in_data':
                self.argument_dict['in_data'] = str(direc)
            elif type == 'aux_data':
                self.argument_dict['aux_data'] = str(direct)
            elif type == 'tmp_data':
                self.argument_dict['tmp_data'] = str(direct)

    def _set_up_basic_options(self, basic_options_frame):
        # basic options

        #imgt or kabat
        scheme_frame = ttk.LabelFrame(basic_options_frame)
        scheme_frame.pack(side=TOP, fill=X, expand=1, padx=5, pady=5)
        self._set_up_scheme_frame(scheme_frame)

        # heavy or light chain
        species_type_frame = ttk.LabelFrame(basic_options_frame)
        species_type_frame.pack(side=TOP, fill=X, expand=1, padx=5, pady=5)
        self._set_up_species_type_frame(species_type_frame)

        # output_type
        output_type_frame = ttk.LabelFrame(basic_options_frame)
        output_type_frame.pack(side=TOP, fill=X, expand=1, padx=5, pady=5)
        self._set_up_output_type_frame(output_type_frame)

        # Number of V D and J genes
        nvdj_type_frame = ttk.LabelFrame(
            basic_options_frame, text="VDJ Matches")
        nvdj_type_frame.pack(side=TOP, fill=X, expand=1, padx=5, pady=5)
        self._set_up_nvdj_type_frame(nvdj_type_frame)

        # Blast options
        blast_options_frame = ttk.LabelFrame(
            basic_options_frame, text="Blast Options")
        blast_options_frame.pack(side=TOP, fill=X, expand=1, padx=5, pady=5)
        self._set_up_blast_options(blast_options_frame)

        # zipped
        zip_bool_type_frame = ttk.LabelFrame(
            basic_options_frame, text="Zip output file")
        zip_bool_type_frame.pack(side=BOTTOM, anchor=SW, padx=5, pady=5)
        self.zip_var = Tkinter.IntVar()
        self.zip_var.set(0)
        zip_chk = ttk.Checkbutton(
            zip_bool_type_frame, onvalue=1, offvalue=0, text="Zip output file",
            variable=self.zip_var, command=lambda: self.zip_var.get())
        zip_chk.pack(side=TOP, anchor=SW)

    def _set_up_scheme_frame(self, scheme_frame):
        self.scheme_var = Tkinter.StringVar()
        self.scheme_var.set("imgt")
        scheme_label = ttk.Label(
            scheme_frame, text="Scheme output:", font=('Arial', 16))
        scheme_label.pack(side=TOP, anchor=NW)
        radio_button_imgt = ttk.Radiobutton(
            scheme_frame, text="IMGT", variable=self.scheme_var, value="imgt")
        radio_button_imgt.pack(side=LEFT, fill=X, expand=1)
        radio_button_kabat = ttk.Radiobutton(
            scheme_frame, text="KABAT", variable=self.scheme_var, value="kabat")
        radio_button_kabat.pack(side=LEFT, fill=X, expand=1)

    def _set_up_chain_type_frame(self, chain_type_frame):
        self.chain_var = Tkinter.StringVar()
        self.chain_var.set("heavy")
        chain_label = ttk.Label(
            chain_type_frame, text="Chain Type:", font=('Arial', 16))
        chain_label.pack(side=TOP, anchor=NW)
        chain_button_heavy = ttk.Radiobutton(
            chain_type_frame, text="HEAVY", variable=self.chain_var, value="heavy")
        chain_button_heavy.pack(side=LEFT, fill=X, expand=1)
        chain_button_light = ttk.Radiobutton(
            chain_type_frame, text="LIGHT", variable=self.chain_var, value="light")
        chain_button_light.pack(side=LEFT, fill=X, expand=1)

    def _set_up_species_type_frame(self, species_type_frame):
        self.species_var = Tkinter.StringVar()
        self.species_var.set("human")
        species_label = ttk.Label(
            species_type_frame, text="Species Type:", font=('Arial', 16))
        species_label.pack(side=TOP, anchor=NW)
        species_button_human = ttk.Radiobutton(
            species_type_frame, text="HUMAN",
            variable=self.species_var, value="human")
        species_button_human.pack(side=LEFT, fill=X, expand=1)
        species_button_mouse = ttk.Radiobutton(
            species_type_frame, text="MOUSE",
            variable=self.species_var, value="mouse")
        species_button_mouse.pack(side=LEFT, fill=X, expand=1)
        species_button_rabbit = ttk.Radiobutton(
            species_type_frame, text="RABBIT",
            variable=self.species_var, value="rabbit", state="disabled")
        species_button_rabbit.pack(side=LEFT, fill=X, expand=1)
        species_button_rat = ttk.Radiobutton(species_type_frame, text="RAT",
                                             variable=self.species_var, value="rat", state="disabled")
        species_button_rat.pack(side=LEFT, fill=X, expand=1)

    def _set_up_output_type_frame(self, output_type_frame):
        self.output_type_var = Tkinter.StringVar()
        self.output_type_var.set("json")
        scheme_label = ttk.Label(
            output_type_frame, text="Output format:", font=('Arial', 16))
        scheme_label.pack(side=TOP, anchor=NW)
        radio_button_json_output = ttk.Radiobutton(
            output_type_frame, text="JSON", variable=self.output_type_var,
            command=lambda suffix="json", self=self: self._update_output(suffix), value="json")
        radio_button_json_output.pack(side=LEFT, fill=X, expand=1)
        radio_button_csv_output = ttk.Radiobutton(
            output_type_frame, text="CSV", variable=self.output_type_var,
            command=lambda suffix="csv", self=self: self._update_output(suffix), value="csv")
        radio_button_csv_output.pack(side=LEFT, fill=X, expand=1)
        radio_button_raw_blast_output = ttk.Radiobutton(
            output_type_frame, text="BLAST", variable=self.output_type_var,
            command=lambda suffix="blast_out", self=self: self._update_output(suffix), value="blast_out")
        radio_button_raw_blast_output.pack(side=LEFT, fill=X, expand=1)

    def _update_output(self, suffix):
        direct = os.path.dirname(self.output_file_entry.get())
        current = os.path.dirname(self.output_file_entry.get()).split('.')[0]
        self.output_file_entry.delete(0, END)
        self.output_file_entry.insert(END, direct + "/" + current + "." + suffix)

    def _set_up_nvdj_type_frame(self, nvdj_type_frame):
        self.v_gene_numb = Tkinter.StringVar()
        numbs = [i for i in xrange(1, 4)]
        v_gene_label = ttk.LabelFrame(nvdj_type_frame, text="V-Gene Matches")
        v_gene_combo = ttk.Combobox(
            v_gene_label, values=numbs, textvariable=self.v_gene_numb)
        v_gene_combo.current(0)
        v_gene_label.pack(side=LEFT, expand=1, pady=5, padx=20, fill=X)
        v_gene_combo.pack(side=TOP, expand=1, pady=5, padx=10, fill=X)

        self.d_gene_numb = Tkinter.StringVar()
        numbs = [i for i in xrange(1, 4)]
        d_gene_label = ttk.LabelFrame(nvdj_type_frame, text="D-Gene Matches")
        d_gene_combo = ttk.Combobox(
            d_gene_label, values=numbs, textvariable=self.d_gene_numb)
        d_gene_combo.current(0)
        d_gene_label.pack(side=LEFT, expand=1, pady=5, padx=20, fill=X)
        d_gene_combo.pack(side=TOP, expand=1, pady=5)

        self.j_gene_numb = Tkinter.StringVar()
        numbs = [i for i in xrange(1, 4)]
        j_gene_label = ttk.LabelFrame(nvdj_type_frame, text="J-Gene Matches")
        j_gene_combo = ttk.Combobox(
            j_gene_label, values=numbs, textvariable=self.j_gene_numb)
        j_gene_combo.current(0)
        j_gene_label.pack(side=LEFT, expand=1, pady=5, padx=20, fill=X)
        j_gene_combo.pack(side=TOP, expand=1, pady=5, padx=10, fill=X)

    def _set_up_blast_options(self, blast_options_frame):
        self.evalue = Tkinter.DoubleVar()
        self.evalue.set(1)
        self.word_size = Tkinter.IntVar()
        self.word_size.set(4)
        self.penalty_mismatch = Tkinter.DoubleVar()
        self.penalty_mismatch.set(-4)
        self.min_d_match = Tkinter.IntVar()
        self.min_d_match.set(5)
        self.proc_count = Tkinter.IntVar()
        self.proc_count.set(cpu_count())

        # evalue
        e_value_label = ttk.LabelFrame(
            blast_options_frame, text="e-Value Threshold")
        e_value_entry = ttk.Entry(e_value_label)
        e_value_entry.insert(0, self.evalue.get())
        e_value_entry.bind('<Return>', self._validate_e_value)
        e_value_entry.bind('<FocusOut>', self._validate_e_value)
        e_value_label.pack(side=LEFT, expand=1, pady=5, padx=5, fill=X)
        e_value_entry.pack(side=TOP, expand=1, pady=5, padx=5, fill=X)

        # word size
        word_size_label = ttk.LabelFrame(
            blast_options_frame, text="Word Size")
        word_size_entry = ttk.Entry(word_size_label)
        word_size_entry.insert(0, self.word_size.get())
        word_size_entry.bind('<Return>', self._validate_word_value)
        word_size_entry.bind('<FocusOut>', self._validate_word_value)
        word_size_label.pack(side=LEFT, expand=1, pady=5, padx=5, fill=X)
        word_size_entry.pack(side=TOP, expand=1, pady=5, padx=5, fill=X)

        penalty_mismatch_label = ttk.LabelFrame(
            blast_options_frame, text="Penalty Mismatch")
        penalty_mismatch_entry = ttk.Entry(penalty_mismatch_label)
        penalty_mismatch_entry.insert(0, self.penalty_mismatch.get())
        penalty_mismatch_entry.bind(
            '<Return>', self._validate_penalty_mismatch_value)
        penalty_mismatch_entry.bind(
            '<FocusOut>', self._validate_penalty_mismatch_value)
        penalty_mismatch_label.pack(side=LEFT, expand=1, pady=5,
                                    padx=5, fill=X)
        penalty_mismatch_entry.pack(side=TOP, expand=1, pady=5,
                                    padx=5, fill=X)
        # Min D Nucleotides
        min_d_match_label = ttk.LabelFrame(
            blast_options_frame, text="Minimal Number of D Nucleotides")
        min_d_match_entry = ttk.Entry(min_d_match_label)
        min_d_match_entry.insert(0, self.min_d_match.get())
        min_d_match_entry.bind(
            '<Return>', self._validate_min_match_value)
        min_d_match_entry.bind(
            '<FocusOut>', self._validate_min_match_value)
        min_d_match_label.pack(side=LEFT, expand=1, pady=5, padx=5, fill=X)
        min_d_match_entry.pack(side=TOP, expand=1, pady=5, padx=5, fill=X)

        # how many cpus to use
        proc_count_label = ttk.LabelFrame(
            blast_options_frame, text="Processors")
        proc_count_entry = ttk.Entry(proc_count_label)
        proc_count_entry.insert(0, self.proc_count.get())
        proc_count_entry.bind(
            '<Return>', self._validate_proc_count_value)
        proc_count_entry.bind(
            '<FocusOut>', self._validate_proc_count_value)
        proc_count_label.pack(side=LEFT, expand=1, pady=5, padx=5, fill=X)
        proc_count_entry.pack(side=TOP, expand=1, pady=5, padx=5, fill=X)

    def _validate_e_value(self, event):
        entry_widget = event.widget
        content = entry_widget.get()
        try:
            if content.strip() == "":
                tkMessageBox.showwarning(
                    "Empty Field",
                    "Enter a value\n")
                entry_widget.insert(0, self.evalue.get())
                entry_widget.focus_set()
            elif float(content) < 0:
                tkMessageBox.showwarning(
                    "To Low",
                    "Value must be positive\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.evalue.get())
                entry_widget.focus_set()
            elif float(content) > 1000:
                tkMessageBox.showwarning(
                    "To High",
                    "Value must be less than 1000\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.evalue.get())
                entry_widget.focus_set()
            else:
                self.evalue.set(float(content))
        except ValueError:
            tkMessageBox.showwarning(
                "Not Float",
                "Value must be a Number\n")
            entry_widget.delete(0, END)
            entry_widget.insert(END, self.evalue.get())
            entry_widget.focus_set()

    def _validate_word_value(self, event):
        entry_widget = event.widget
        content = entry_widget.get()
        try:
            if content.strip() == "":
                tkMessageBox.showwarning(
                    "Empty Field",
                    "Enter a value\n")
                entry_widget.insert(0, self.word_size.get())
                entry_widget.focus_set()
            elif int(content) < 1:
                tkMessageBox.showwarning(
                    "To Low",
                    "Value must be greater than 1\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.word_size.get())
                entry_widget.focus_set()

            elif int(content) > 10:
                tkMessageBox.showwarning(
                    "To High",
                    "Value must be less than 10\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.word_size.get())
                entry_widget.focus_set()
            else:
                self.evalue.set(int(content))
        except ValueError:
            tkMessageBox.showwarning(
                "Not Int",
                "Value must be an integer\n")
            entry_widget.delete(0, END)
            entry_widget.insert(END, self.word_size.get())
            entry_widget.focus_set()

    def _validate_penalty_mismatch_value(self, event):
        entry_widget = event.widget
        content = entry_widget.get()
        try:
            if content.strip() == "":
                tkMessageBox.showwarning(
                    "Empty Field",
                    "Enter a value\n")
                entry_widget.insert(0, self.penalty_mismatch.get())
                entry_widget.focus_set()
            elif float(content) < -6.0:
                tkMessageBox.showwarning(
                    "To Low",
                    "Value must be greater than -6\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.penalty_mismatch.get())
                entry_widget.focus_set()

            elif float(content) > 0:
                tkMessageBox.showwarning(
                    "To High",
                    "Value must be less than 0\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.penalty_mismatch.get())
                entry_widget.focus_set()
            else:
                self.evalue.set(float(content))
        except ValueError:
            tkMessageBox.showwarning(
                "Not Float",
                "Value must be a Number\n")
            entry_widget.delete(0, END)
            entry_widget.insert(END, self.penalty_mismatch.get())
            entry_widget.focus_set()

    def _validate_min_match_value(self, event):
        entry_widget = event.widget
        content = entry_widget.get()
        try:
            if content.strip() == "":
                tkMessageBox.showwarning(
                    "Empty Field",
                    "Enter a value\n")
                entry_widget.insert(0, self.min_d_match.get())
                entry_widget.focus_set()
            elif int(content) < 5:
                tkMessageBox.showwarning(
                    "To Low",
                    "Value must be greater than 5\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.min_d_match.get())
                entry_widget.focus_set()

            elif int(content) > 15:
                tkMessageBox.showwarning(
                    "To High",
                    "Value must be less than 15\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.min_d_match.get())
                entry_widget.focus_set()
            else:
                self.evalue.set(int(content))
        except ValueError:
            tkMessageBox.showwarning(
                "Not Int",
                "Value must be an integer\n")
            entry_widget.delete(0, END)
            entry_widget.insert(END, self.min_d_match.get())
            entry_widget.focus_set()

    def _validate_proc_count_value(self, event):
        entry_widget = event.widget
        content = entry_widget.get()
        try:
            if content.strip() == "":
                tkMessageBox.showwarning(
                    "Empty Field",
                    "Enter a value\n")
                entry_widget.insert(0, self.proc_count.get())
                entry_widget.focus_set()
            elif int(content) < 0:
                tkMessageBox.showwarning(
                    "To Low",
                    "Value must be positive\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.proc_count.get())
                entry_widget.focus_set()

            elif int(content) > self.proc_count.get():
                tkMessageBox.showwarning(
                    "To High",
                    "Value is higher than the amount of processors you have\n")
                entry_widget.delete(0, END)
                entry_widget.insert(END, self.proc_count.get())
                entry_widget.focus_set()
            else:
                self.evalue.set(int(content))
        except ValueError:
            tkMessageBox.showwarning(
                "Not Int",
                "Value must be an integer\n")
            entry_widget.delete(0, END)
            entry_widget.insert(END, self.proc_count.get())
            entry_widget.focus_set()

    def _create_format_output(self, main_notebook_frame):
        # secon tab
        output_frame = ttk.LabelFrame(main_notebook_frame)
        output_frame.pack(side=TOP, expand=1, fill=BOTH, padx=10, pady=10)
        self._make_output_file(output_frame)
        self._fill_output_format_tab(output_frame)
        main_notebook_frame.add(
            output_frame, text="Output Options", underline=0, padding=2)

    def _make_output_file(self, output_frame):
        output_file_frame = ttk.LabelFrame(output_frame)
        output_file_frame.pack(side=TOP, fill=X, padx=10, pady=10)
        output_file_label = ttk.Label(
            output_file_frame, text='Enter Output File Name',
            font=('Arial', 26))
        output_file_label.pack(side=TOP, anchor=NW, padx=5, pady=5)

        self.output_file_entry = ttk.Entry(output_file_frame, width=10)
        self.output_file_entry.delete(0, END)
        self.output_file_entry.insert(END, self.argument_dict['output_file'] +
                                      "." + str(self.output_type_var.get()))
        output_file_entry_button = ttk.Button(
            output_file_frame, text="Browse...",
            command=lambda entry=self.output_file_entry: self._enter_output(entry))
        self.output_file_entry.pack(side=LEFT, padx=3, expand=1, fill=X)
        output_file_entry_button.pack(side=LEFT, fill=X)

    def _fill_output_format_tab(self, output_frame):
        # fill output_format_tab from another dictionary
        output_fields_frame = ttk.LabelFrame(output_frame)
        output_fields_top_label = ttk.Label(
            output_fields_frame, text="Select Output Fields", font=('Arial', 20))
        output_fields_top_label.pack(side=TOP, padx=3, pady=3, anchor=NW)
        output_fields_frame.pack(
            side=TOP, fill=BOTH, expand=1, padx=2)

        # general options
        general_frame = ttk.LabelFrame(output_fields_frame)
        general_label = ttk.Label(
            general_frame, text="General fields:", font=('Arial', 20))
        general_label.pack(side=TOP, anchor=NW, padx=5, pady=5)
        _general_options = all_checkboxes_dict['general']
        self.general_class = Checkbar(parent=general_frame, picks=[
                                      (i['formal'], i['default'], i['json_key']) for i in _general_options])
        general_frame.pack(side=TOP, expand=1, fill=X)

        # nucleotide
        nucleotide_frame = ttk.LabelFrame(output_fields_frame)
        nucleotide_label = ttk.Label(nucleotide_frame, font=('Arial', 20),
                                     text="Nucleotide Specific:")
        nucleotide_label.pack(side=TOP, anchor=NW, padx=5, pady=5)
        _nucleotide_options = all_checkboxes_dict['nucleotide']
        self.nucleotide_class = Checkbar(parent=nucleotide_frame, picks=[
            (i['formal'], i['default'], i['json_key']) for i in _nucleotide_options])
        nucleotide_frame.pack(side=TOP, fill=X, expand=1)

        # Translation Specific
        amino_frame = ttk.LabelFrame(output_fields_frame)
        amino_label = ttk.Label(amino_frame, font=('Arial', 20),
                                text="Translation Specific:")
        amino_label.pack(side=TOP, anchor=NW)
        _amino_options = all_checkboxes_dict['amino']
        self.amino_class = Checkbar(parent=amino_frame, picks=[(i['formal'], i['default'], i['json_key']) for i in _amino_options])
        amino_frame.pack(side=TOP, fill=X, expand=1)

        # Alignment_frame
        alignment_frame = ttk.LabelFrame(output_fields_frame)
        alignment_label = ttk.Label(alignment_frame, font=('Arial', 20),
                                    text="Alignment Information:")
        alignment_label.pack(side=TOP, anchor=NW)

        # subframe in alignment frame
        total_alignment_frame = ttk.LabelFrame(alignment_frame)
        total_alignment_label = ttk.Label(total_alignment_frame, font=('Arial', 16),
                                          text="Total Alignments")
        total_alignment_label.pack(side=TOP, anchor=NW)
        _total_options = all_checkboxes_dict['total_alignments']
        self.total_alignments_class = Checkbar(parent=total_alignment_frame,
                                               picks=[(i['formal'], i['default'], i['json_key']) for i in _total_options])
        total_alignment_frame.pack(side=TOP, expand=1, fill=X)

        fw1_alignment_frame = ttk.LabelFrame(alignment_frame)
        fw1_alignment_label = ttk.Label(fw1_alignment_frame, font=('Arial', 16),
                                        text="FW1 Alignments")
        fw1_alignment_label.pack(side=TOP, anchor=NW)
        _fw1_options = all_checkboxes_dict['fw1_alignments']
        self.fw1_alignments_class = Checkbar(parent=fw1_alignment_frame,
                                             picks=[(i['formal'], i['default'], i['json_key']) for i in _fw1_options])
        fw1_alignment_frame.pack(side=TOP, expand=1, fill=X)

        fw2_alignment_frame = ttk.LabelFrame(alignment_frame)
        fw2_alignment_label = ttk.Label(fw2_alignment_frame, font=('Arial', 16),
                                        text="FW2 Alignments")
        fw2_alignment_label.pack(side=TOP, anchor=NW)
        _fw2_options = all_checkboxes_dict['fw2_alignments']
        self.fw2_alignments_class = Checkbar(parent=fw2_alignment_frame,
                                             picks=[(i['formal'], i['default'], i['json_key']) for i in _fw2_options])
        fw2_alignment_frame.pack(side=TOP, expand=1, fill=X)

        fw3_alignment_frame = ttk.LabelFrame(alignment_frame)
        fw3_alignment_label = ttk.Label(fw3_alignment_frame, font=('Arial', 16),
                                        text="FW3 Alignments")
        fw3_alignment_label.pack(side=TOP, anchor=NW)
        _fw3_options = all_checkboxes_dict['fw3_alignments']
        self.fw3_alignments_class = Checkbar(parent=fw3_alignment_frame,
                                             picks=[(i['formal'], i['default'], i['json_key']) for i in _fw3_options])
        fw3_alignment_frame.pack(side=TOP, expand=1, fill=X)

        cdr1_alignment_frame = ttk.LabelFrame(alignment_frame)
        cdr1_alignment_label = ttk.Label(cdr1_alignment_frame, font=('Arial', 16),
                                         text="CDR1 Alignments")
        cdr1_alignment_label.pack(side=TOP, anchor=NW)
        _cdr1_options = all_checkboxes_dict['cdr1_alignments']
        self.cdr1_alignments_class = Checkbar(parent=cdr1_alignment_frame,
                                              picks=[(i['formal'], i['default'], i['json_key']) for i in _cdr1_options])
        cdr1_alignment_frame.pack(side=TOP, expand=1, fill=X)

        cdr2_alignment_frame = ttk.LabelFrame(alignment_frame)
        cdr2_alignment_label = ttk.Label(cdr2_alignment_frame, font=('Arial', 16),
                                         text="CDR2 Alignments")
        cdr2_alignment_label.pack(side=TOP, anchor=NW)
        _cdr2_options = all_checkboxes_dict['cdr2_alignments']
        self.cdr2_alignments_class = Checkbar(parent=cdr2_alignment_frame,
                                              picks=[(i['formal'], i['default'], i['json_key']) for i in _cdr2_options])
        cdr2_alignment_frame.pack(side=TOP, expand=1, fill=X)

        cdr3_alignment_frame = ttk.LabelFrame(alignment_frame)
        cdr3_alignment_label = ttk.Label(cdr3_alignment_frame, font=('Arial', 16),
                                         text="CDR3 Alignments")
        cdr3_alignment_label.pack(side=TOP, anchor=NW)
        _cdr3_options = all_checkboxes_dict['cdr3_alignments']
        self.cdr3_alignments_class = Checkbar(parent=cdr3_alignment_frame,
                                              picks=[(i['formal'], i['default'], i['json_key']) for i in _cdr3_options])
        cdr3_alignment_frame.pack(side=TOP, expand=1, fill=X)

        alignment_frame.pack(side=TOP, expand=1, fill=X)

        hits_frame = ttk.LabelFrame(output_fields_frame)
        hits_label = ttk.Label(hits_frame, font=('Arial', 20),
                               text="Gene Hits:")
        hits_label.pack(side=TOP, anchor=NW)

        # subframe in alignment frame
        v_hit_frame = ttk.LabelFrame(hits_frame)
        v_hit_label = ttk.Label(v_hit_frame, font=('Arial', 16),
                                text="V-Gene")
        v_hit_label.pack(side=TOP, anchor=NW)
        _v_hits_options = all_checkboxes_dict['v_hits']
        self.v_hits_class = Checkbar(parent=v_hit_frame,
                                     picks=[(i['formal'], i['default'], i['json_key']) for i in _v_hits_options])
        v_hit_frame.pack(side=TOP, expand=1, fill=X)

        d_hit_frame = ttk.LabelFrame(hits_frame)
        d_hit_label = ttk.Label(d_hit_frame, font=('Arial', 16),
                                text="D-Gene")
        d_hit_label.pack(side=TOP, anchor=NW)
        _d_hits_options = all_checkboxes_dict['d_hits']
        self.d_hits_class = Checkbar(parent=d_hit_frame,
                                     picks=[(i['formal'], i['default'], i['json_key']) for i in _d_hits_options])
        d_hit_frame.pack(side=TOP, expand=1, fill=X)

        j_hit_frame = ttk.LabelFrame(hits_frame)
        j_hit_label = ttk.Label(j_hit_frame, font=('Arial', 16),
                                text="J-Gene")
        j_hit_label.pack(side=TOP, anchor=NW)
        _j_hits_options = all_checkboxes_dict['j_hits']
        self.j_hits_class = Checkbar(parent=j_hit_frame,
                                     picks=[(i['formal'], i['default'], i['json_key']) for i in _j_hits_options])
        j_hit_frame.pack(side=TOP, expand=1, fill=X)
        hits_frame.pack(side=TOP, expand=1, fill=X)

    def _enter_output(self, entry):
        fo = None
        opts = {'title': "Select output file to open...",
                'initialfile': entry.get(),
                'initialdir': self._user_directory}
        fo = filedialog.asksaveasfilename(**opts)
        if fo:
            entry.delete(0, END)
            entry.insert(END, fo)
            self.argument_dict['output_file'] = str(fo)

    def _create_readme(self, notebook_frame):
        readme_frame = ttk.Frame(notebook_frame, name="r_frame")
        # scroled_widget = ttk.ScrolledWindow(readme_frame,scrollbar='auto')
        # window = scroled.window
        vertical_scroll_frame = vsf(readme_frame)
        vertical_scroll_frame.pack(side=TOP, expand=1, fill=BOTH, anchor=NW)
        vsf_label = ttk.Label(
            vertical_scroll_frame.interior, text=open(self._directory_name + '/README_gui.txt').readlines(), anchor=N)
        # scroled_widget.pack(side=TOP, fill=BOTH, expand=1)
        vsf_label.pack(side=TOP, fill=BOTH, expand=1, anchor=NW)
        notebook_frame.add(readme_frame, text="Readme", underline=0, padding=2)

    def _update(self):
        import gui_setup
        gui_setup.main_refresh(self.root, gui_setup)

    def execute(self):
        # okay here we go
        if not self.argument_dict['query']:
            tkMessageBox.showwarning(
                "Input Missing",
                "At the very least we need a fasta\n")
        output_options = [self.general_class.state(), self.nucleotide_class.state(),
                          self.amino_class.state(), self.total_alignments_class.state(), self.fw1_alignments_class.state(),
                          self.fw2_alignments_class.state(), self.fw3_alignments_class.state(), self.cdr1_alignments_class.state(),
                          self.cdr2_alignments_class.state(), self.cdr3_alignments_class.state(),
                          self.v_hits_class.state(), self.d_hits_class.state(), self.j_hits_class.state()]

        blast_args_dict = {
            '-query': "",
            '-organism': self.species_var.get(),
            '-num_alignments_V': self.v_gene_numb.get(),
            '-num_alignments_D': self.d_gene_numb.get(),
            '-num_alignments_J': self.j_gene_numb.get(),
            '-min_D_match': str(self.min_d_match.get()),
            '-D_penalty': str(int(self.penalty_mismatch.get())),
            '-domain_system': self.scheme_var.get(),
            '-out': "",
            '-evalue': str(self.evalue.get()),
            '-word_size': str(self.word_size.get()),
            '-max_target_seqs': str(500),
            '-germline_db_V': "{0}{1}_gl_V".format(
                self.argument_dict['database'], self.species_var.get()),
            '-germline_db_D': "{0}{1}_gl_D".format(
                self.argument_dict['database'], self.species_var.get()),
            '-germline_db_J': "{0}{1}_gl_J".format(
                self.argument_dict['database'], self.species_var.get()),
            '-auxiliary_data': "{0}{1}_gl.aux".format(
                self.argument_dict['aux_data'], self.species_var.get()),
            '-domain_system': self.scheme_var.get(),
            '-outfmt': str(7)
        }

        output_options_dict = {
            'final_outfile': self.argument_dict['output_file'],
            'num_procs': self.proc_count.get(),
            'pre_split_up_input': self.argument_dict['query'],
            'zip_bool': self.zip_var.get(),
            'tmp_data_directory': self.argument_dict['tmp_data'],
            'internal_data_directory': self.argument_dict['in_data'],
            'output_type': self.output_type_var.get(),
            'output_options': output_options
        }
        execute(blast_args_dict, output_options_dict)


def main_refresh(root, gui_setup):
    reload(gui_setup)
    root.destroy()
    gui_setup.main()


def main():
    root = Tkinter.Tk()
    pyigblast_class = pyigblast_gui(root)
    root.mainloop()


class Checkbar():

    def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
        self.vars = {}
        for i, pick in enumerate(picks):
            json_key = pick[2]
            print json_key
            var = Tkinter.IntVar()
            var.set(int(pick[1]))
            chk = ttk.Checkbutton(parent, onvalue=1, offvalue=0, text=pick[
                                  0], variable=var, command=lambda: self.state())
            chk.pack(side=LEFT, fill=X, expand=1)
            self.vars[pick[0]] = {"state": var, "json_key": json_key}

    def state(self):
        states_dict = {}
        for var in self.vars:
            states_dict[var] = {"state": self.vars[var]['state'].get(), "json_key": self.vars[var]['json_key']}
        print states_dict
        return states_dict

if __name__ == '__main__':
    main()

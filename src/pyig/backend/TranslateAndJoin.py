import sys
import warnings
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
from Isotype import get_isotype
warnings.filterwarnings('ignore')


class TranslateAndJoin():

    '''The heavy lifting is done by this class, the IgO is the 'super' class from IgBlast output
    access to all member variables of IgO. Therefore we can just change the output dictionary in
    that instance'''

    def __init__(self, IgO):
        '''Takes in superclass instance IgO'''
        self.fudge_factor_add = True
        self.species = 'human'
        self.IgO = IgO
        self.output = IgO.output
        # We need all these things again
        self.seq_id = self.output['Sequence Id']
        self.debug = IgO.debug

        '''The fudge factor simply asks if the V gene started matching in the middle of codon,
        if it does, then it increases it by one until the first reading frame of a codon can be found. 
        It is always smart to start matching at the start of every codon instead of right in the middle,
        that will screw up all the frameworks'''
        self.fudge_factor = 0
        try:
            v_gene_start = self.output[
                'V-Gene Rank_1']['V-Gene Rank_1 S. start'] - 1
            while True:
                if v_gene_start % 3 == 0:
                    break
                else:
                    if self.debug:
                        print "Increasing Fudge Factor by 1, total {}".format(self.fudge_factor)
                    v_gene_start += 1
                    self.fudge_factor += 1
        except:
            print "No V Gene Alignment, Skipping"

        # First things first, let's make sure we get the query in the right
        # orientation.
        if self.output['Strand'] == '+':
            self.sequence = self.output['Query Sequence']
        elif self.output['Strand'] == '-':
            self.sequence = str(
                Seq(self.output['Query Sequence']).reverse_complement())

        # Goes through all 4 frameworks and 3 cdrs to set and translate, if they are empty we simply
        # pass and leave that part empty in the output
        try:
            self.framework1_set_and_translate()
            self.fudge_factor_add = False
        except (KeyError, ValueError):
            if self.debug:
                print "FW1 does not exist for {0}".format(self.seq_id)
            pass

        try:
            self.CDR1_set_and_translate()
            self.fudge_factor_add = False
        except (KeyError, ValueError):
            if self.debug:
                print "CDR1 does not exist for {0}".format(self.seq_id)
            pass

        try:
            self.framework2_set_and_translate()
            self.fudge_factor_add = False
        except (KeyError, ValueError):
            if self.debug:
                print "FW2 does not exist for {0}".format(self.seq_id)
            pass

        try:
            self.CDR2_set_and_translate()
            self.fudge_factor_add = False
        except (KeyError, ValueError):
            if self.debug:
                print "CDR2 does not exist for {0}".format(self.seq_id)
            pass

        try:
            self.framework3_set_and_translate()
            self.fudge_factor_add = False
        except (KeyError, ValueError):
            if self.debug:
                print "FW3 does not exist for {0}".format(self.seq_id)
            pass

        try:
            self.CDR3_set_and_translate()
            self.fudge_factor_add = False
        except (KeyError, ValueError):
            if self.debug:
                print "CDR3 does not exist for {0}".format(self.seq_id)
            pass

        try:
            self.FW4_set_and_translate()
            self.fudge_factor_add = False
        except (KeyError, ValueError):
            if self.debug:
                print "FW4 does not exist for {0}".format(self.seq_id)
            pass

        # Finally Set Isotype based on Raw Sequence, Probably doesn't need any try or except
        self.set_isotype()

    def set_isotype(self):
        _seq = self.output['Query Sequence']
        _iso = get_isotype(_seq)
        if self.debug:
            print "{} isotype - {}".format(self.output['Sequence Id'], _iso)
        self.output['Isotype'] = _iso

    #_from - nucleotide position start
    #_to - nucleotide position end
    def framework1_set_and_translate(self):
        _from = int(self.output["FW1 Alignment From"])
        if self.fudge_factor_add:
            if self.debug:
                print "Adding fudge factor to FW1"
            _from += self.fudge_factor
        _to = int(self.output["FW1 Alignment To"])
        # make a sequence
        self.output['Framework 1 Nucleotides'] = self.sequence[_from - 1:_to]
        # translate
        self.output['Framework 1 AA'] = str(
            Seq(self.output['Framework 1 Nucleotides'], IUPAC.ambiguous_dna).translate())
        # get length
        self.output['Framework 1 AA Length'] = len(
            self.output['Framework 1 AA'])

    # same
    def framework2_set_and_translate(self):
        _from = int(self.output["FW2 Alignment From"])
        if self.fudge_factor_add:
            if self.debug:
                print "Adding fudge factor to FW2"
            _from += self.fudge_factor
        _to = int(self.output["FW2 Alignment To"])
        self.output['Framework 2 Nucleotides'] = self.sequence[_from - 1:_to]
        self.output['Framework 2 AA'] = str(
            Seq(self.output['Framework 2 Nucleotides'], IUPAC.ambiguous_dna).translate())
        self.output['Framework 2 AA Length'] = len(
            self.output['Framework 2 AA'])

    # same
    def framework3_set_and_translate(self):
        _from = int(self.output["FW3 Alignment From"])
        if self.fudge_factor_add:
            if self.debug:
                print "Adding fudge factor to FW3"
            _from += self.fudge_factor
        _to = int(self.output["FW3 Alignment To"])
        self.output['Framework 3 Nucleotides'] = self.sequence[_from - 1:_to]
        self.output['Framework 3 AA'] = str(
            Seq(self.output['Framework 3 Nucleotides'], IUPAC.ambiguous_dna).translate())
        self.output['Framework 3 AA Length'] = len(
            self.output['Framework 3 AA'])

    # same
    def CDR1_set_and_translate(self):
        _from = int(self.output["CDR1 Alignment From"])
        if self.fudge_factor_add:
            if self.debug:
                print "Adding fudge factor to CDR1"
            _from += self.fudge_factor
        _to = int(self.output["CDR1 Alignment To"])
        self.output['CDR1 Nucleotides'] = self.sequence[_from - 1:_to]
        self.output['CDR1 AA'] = str(
            Seq(self.output['CDR1 Nucleotides'], IUPAC.ambiguous_dna).translate())
        self.output['CDR1 AA Length'] = len(self.output['CDR1 AA'])

    # same
    def CDR2_set_and_translate(self):
        _from = int(self.output["CDR2 Alignment From"])
        if self.fudge_factor_add:
            if self.debug:
                print "Adding fudge factor to CDR2"
            _from += self.fudge_factor
        _to = int(self.output["CDR2 Alignment To"])
        self.output['CDR2 Nucleotides'] = self.sequence[_from - 1:_to]
        self.output['CDR2 AA'] = str(
            Seq(self.output['CDR2 Nucleotides'], IUPAC.ambiguous_dna).translate())
        self.output['CDR2 AA Length'] = len(self.output['CDR2 AA'])

    # hard part
    def CDR3_set_and_translate(self):
        # first get the gene first ranked
        j_gene = self.output['J-Gene Rank_1']['J-Gene Rank_1 Subject id']
        try:
            # Then find length until it hits end of cdr3 which is defined in a
            # datafile
            j_length = int(self.IgO.j_trans[j_gene])
        except KeyError:
            raise Exception(
                "Germline Gene {0} not found in CDR3 Lenth Description, this needs to be set to determine when the J reading frame ends for the CDR3, refer to documentation for setting this gene".format(j_gene))
            sys.exit(1)

        # j_begin is where on the sequence the j gene sits
        # j_end is how many nucleotides in on the j gene does it sit
        j_begin = int(
            self.output['J-Gene Rank_1']['J-Gene Rank_1 Q. start']) - 1
        j_end = int(self.output['J-Gene Rank_1']['J-Gene Rank_1 S. start'])
        # do the arithemetic to find the end - see documentation for more help
        j_end = (j_length - j_end) + j_begin

        if self.output['CDR3 Alignment From']:
            v_part_from = int(self.output['CDR3 Alignment From']) - 1
            #v_part_to = int(self.output['CDR3 Alignment To'])
            #v_part_nuc = self.sequence[v_part_from - 1:v_part_to]

        # sometimes there is no v_part, but we can get it from the junction
        # part of igblast
        else:
            v_part_from = self.sequence.index(self.IgO.junction_merged[5:]) - 1

        self.output['CDR3 Nucleotides'] = self.sequence[v_part_from:j_end]
        self.output['CDR3 AA'] = str(
            Seq(self.output['CDR3 Nucleotides'], IUPAC.ambiguous_dna).translate())
        self.output['CDR3 AA Length'] = len(self.output['CDR3 AA'])

    # same as fw1-3 and cdr1-2
    def FW4_set_and_translate(self):
        _from = self.sequence.index(
            self.output['CDR3 Nucleotides']) + len(self.output['CDR3 Nucleotides'])
        _to = int(self.output['J-Gene Rank_1']['J-Gene Rank_1 Q. end'])
        self.output['Framework 4 Nucleotides'] = self.sequence[_from - 2:_to]
        self.output['Framework 4 AA'] = str(
            Seq(self.output['Framework 4 Nucleotides'], IUPAC.ambiguous_dna).translate())
        self.output['Framework 4 AA Length'] = len(
            self.output['Framework 4 AA'])

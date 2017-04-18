from __future__ import division

import numpy as np
import os
import pysam as ps
from Bio import SeqIO
import Bio as bio
from io import StringIO
import random as rd
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

#set seeds

np.random.seed(42)
rd.seed(42)

#versions used
#pysam 0.10.0
#Biopython: 1.68
#numpy




########################################################################################################################
#
# TO-DO:
#   -correct the single end IDs
#   -ecdf() ecDNA length
#   - Check that reads come from repeats: LTR
#   - Fix right split read
#   - FIx 271


__author__ = 'Inigo Prada Luengo xsh723@alumni.ku.dk'

__help__ = ['Script that simulates single end and paired-end eccDNA']

__external_packages__ = 'this program uses pysam version: %s, Biopython version: %s and numpy version %s' % (ps.__version__, 
bio.__version__ , np.__version__)
__external_packages_used__ = 'this program was develop with pysam version: 0.10.0, Biopython version: 1.68 and numpy version 1.12.0'


def sim_ecc_reads(genome_fasta,path_to_genome_fasta,read_length,paired_end,directory,spawn_reads,temp_fastq,insert_size,errors):
    """Function that takes as arguments a genome fasta file, weights each chromosome based on the length
    and simulates single end eccDNA reads
     """

    # Get the length of the chromosomes and store them in a sequence dictionary
    chromosomes = {}
    whole_genome_len = 0
    print("getting contig lengths")
    for rec in SeqIO.parse(genome_fasta, 'fasta'):
        name = rec.id
        seqLen = len(rec)
        whole_genome_len += seqLen
        chromosomes[name] = seqLen
    print(chromosomes)
    #weight each chromosome based on the length, thats the probability of a eccDNA being generated by a given chromosome

    print("weighting chromosomes")
    weighted_chromosomes = {}
    for contigs in chromosomes:
        weighted_chromosomes[contigs] = chromosomes[contigs]/whole_genome_len


    contig_list = []
    weights = []
    for contigs, value in weighted_chromosomes.items():
        weights.append(value)
        contig_list.append(contigs)



    #Simulate the reads:



    os.chdir(directory)

    if paired_end == True:
        paired_end_fastq_1 = open("example_1.fastq","w")
        paired_end_fastq_2 = open("example_2.fastq","w")
    else:

        single_end_fastq = open(temp_fastq, "w")

    genome_fasta.close()

    set_of_reads = []
    set_of_left_reads = []
    set_of_right_reads = []
    i = spawn_reads[0] -1
    circle_number = 0
    while i < spawn_reads[-1] +1:
        #decide the chromosome
        chr = np.random.choice(contig_list, p=weights)

        # decide ecDNA length

        circle_length = rd.randint(150,200)


        # linear decrease in coverage based on circle length

        coverage = np.arange(1, 41, 1)
        #reverse the list
        coverage = coverage[::-1]
        length = np.arange(100, 100000, 2500)
        circle_number +=1
        index = np.abs(length - 50000).argmin()
        mean_cov = coverage[index]

        # compute the coverage taking into account the linear decrease

        if paired_end == True:

            rounds_of_sim = (circle_length * mean_cov)/(read_length*2)
        else:
            rounds_of_sim = (circle_length * mean_cov) /read_length





        # take in to account short length contigs

        chr_pos_start =  rd.randint(0,(chromosomes[chr] - circle_length))
        if chromosomes[chr] == (chromosomes[chr] - circle_length):
            chr_pos_end = chromosomes[chr]
        else:
            chr_pos_end = chr_pos_start + circle_length


        #account for paired end or single end data

        #sim paired end

        for each_sim in range(0,round(int(rounds_of_sim))):

            if paired_end == True:

                if errors == True:



                    if ((i + 1) / 1000000).is_integer() == False:
                        try:
                            # simulate reads and save them to ram
                            print(i)
                            # create object
                            new_read = sim_paired_end(i, insert_size, path_to_genome_fasta, chr, chr_pos_start,
                                                      chr_pos_end, read_length, circle_number)
                            # sim the read
                            get_seq = new_read.simulate_read()
                            # put it in fastq format
                            simulated_reads = sim_paired_end.simulate_read_with_errors(new_read, get_seq[0], get_seq[1],
                                                                                   get_seq[2])
                            # save the read
                            set_of_left_reads.append(simulated_reads[0])
                            set_of_right_reads.append(simulated_reads[1])
                            i += 1

                        except:
                            pass




                    else:
                        try:
                            # simulate reads and save to disk
                            print(i)

                            new_read = sim_paired_end(i, insert_size, path_to_genome_fasta, chr, chr_pos_start,
                                                      chr_pos_end, read_length, circle_number)
                            get_seq = new_read.simulate_read()
                            simulated_reads = sim_paired_end.simulate_read_with_errors(new_read, get_seq[0], get_seq[1],
                                                                                   get_seq[2])
                            set_of_left_reads.append(simulated_reads[0])
                            set_of_right_reads.append(simulated_reads[1])

                            # save to disk
                            SeqIO.write(set_of_left_reads, paired_end_fastq_1, "fastq")
                            SeqIO.write(set_of_right_reads, paired_end_fastq_2, "fastq")

                            i += 1
                            # sim the first read of the list
                            new_read = sim_paired_end(i, insert_size, path_to_genome_fasta, chr, chr_pos_start,
                                                      chr_pos_end, read_length, circle_number)
                            get_seq = new_read.simulate_read()
                            simulated_reads = sim_paired_end.simulate_read_with_errors(new_read, get_seq[0], get_seq[1],
                                                                                   get_seq[2])

                            set_of_left_reads = [simulated_reads[0]]
                            set_of_right_reads = [simulated_reads[1]]
                            i += 1
                        except:
                            pass

                else:

                    if ((i + 1) / 1000000).is_integer() == False:
                        try:
                            #simulate reads and save them to ram
                            print(i)
                            #create object
                            new_read = sim_paired_end(i, insert_size, path_to_genome_fasta, chr, chr_pos_start,
                                                      chr_pos_end, read_length, circle_number)
                            #sim the read
                            get_seq = new_read.simulate_read()
                            #put it in fastq format
                            simulated_reads = sim_paired_end.simulate_perfect_read(new_read,get_seq[0], get_seq[1], get_seq[2])
                            #save the read
                            set_of_left_reads.append(simulated_reads[0])
                            set_of_right_reads.append(simulated_reads[1])
                            i +=1
                        except:
                            pass

                    else:
                        try:
                            #simulate reads and save to disk
                            print(i)

                            new_read = sim_paired_end(i, insert_size, path_to_genome_fasta, chr, chr_pos_start,
                                                      chr_pos_end, read_length, circle_number)
                            get_seq = new_read.simulate_read()
                            simulated_reads = sim_paired_end.simulate_perfect_read(new_read, get_seq[0], get_seq[1],
                                                                                   get_seq[2])
                            set_of_left_reads.append(simulated_reads[0])
                            set_of_right_reads.append(simulated_reads[1])

                            #save to disk
                            SeqIO.write(set_of_left_reads,paired_end_fastq_1 , "fastq")
                            SeqIO.write(set_of_right_reads, paired_end_fastq_2, "fastq")

                            i += 1
                            #sim the first read of the list
                            new_read = sim_paired_end(i, insert_size, path_to_genome_fasta, chr, chr_pos_start,
                                                      chr_pos_end, read_length, circle_number)
                            get_seq = new_read.simulate_read()
                            simulated_reads = sim_paired_end.simulate_perfect_read(new_read, get_seq[0], get_seq[1],
                                                                                   get_seq[2])

                            set_of_left_reads = [simulated_reads[0]]
                            set_of_right_reads = [simulated_reads[1]]
                            i +=1
                        except:
                            pass



            #sim single end
            else:
                if ((i + 1) / 2000000).is_integer() == False:
                    try:
                        print(i)
                        new_read = sim_single_end(i,path_to_genome_fasta, chr, chr_pos_start, chr_pos_end, read_length, circle_number)
                        set_of_reads.append(new_read)
                        i += 1
                    except:
                        pass

                else:
                    try:
                        print(i)
                        new_read = sim_single_end(i,path_to_genome_fasta, chr, chr_pos_start, chr_pos_end, read_length, circle_number)
                        SeqIO.write(set_of_reads,single_end_fastq,"fastq")
                        i +=1
                        new_read = sim_single_end(i, path_to_genome_fasta, chr, chr_pos_start, chr_pos_end, read_length,
                                                  circle_number)
                        set_of_reads = [new_read]
                        i += 1
                    except:
                        pass




    return("process finished")


def sim_single_end(read_number,genome_fa,chr,chr_pos_start,chr_pos_end,read_length,circle):
    # create fastafile object
    fastafile = ps.FastaFile(genome_fa)
    #pick a random position in the circle
    start = np.random.randint(chr_pos_start,(chr_pos_end+1))
    end = start + read_length
    #if the end position if bigger than the chr_end_position, that indicates a circle
    if end > chr_pos_end:
        #back spliced_read


        #number of right nucleotides to take
        right_backspliced = end - chr_pos_end
        #right nucleotides position
        right_nucleotides = chr_pos_start + right_backspliced
        # get the right split read
        right_split_read = fastafile.fetch(chr, chr_pos_start,right_nucleotides)
        #left split read nucleotide position
        left_nucleotides_start = chr_pos_end - (read_length - right_backspliced)
        #get left split read
        left_split_read = fastafile.fetch(chr, left_nucleotides_start, chr_pos_end)
        #put all together
        total_read = left_split_read + right_split_read
        seq_id = "%s|%s|%s:%s-%s:%s|1|%s" % (read_number,chr,left_nucleotides_start,chr_pos_end,chr_pos_start,right_nucleotides,circle)


    else:
        #sample normal read
        seq_id = "%s|%s|%s:%s|0|%s" % (read_number,chr,start,end,circle)
        total_read = fastafile.fetch(chr, start,end)


    #get each entry of the fastq file
    #right now, the quality is maximum
    quality = "I" * read_length
    #put all together
    fastq_string = "@%s\n%s\n+\n%s\n" % (seq_id, total_read, quality)
    new_record = SeqIO.read(StringIO(fastq_string), "fastq")
    return(new_record)







class sim_paired_end:

    #init the class
    def __init__(self,read_number,insert_size,genome_fa,chr,chr_pos_start,chr_pos_end,read_length,circle_id):
        self.read_number = read_number
        self.insert_size = insert_size
        self.genome_fa = genome_fa
        self.chr = chr
        self.chr_pos_start = chr_pos_start
        self.chr_pos_end = chr_pos_end
        self.read_length = read_length
        self.circle_id = circle_id

    def simulate_read(self):
        """Function that simulates perfect paired-end reads"""
        fastafile = ps.FastaFile(self.genome_fa)
        # left split read
        insert = int(np.random.normal(self.insert_size, (self.insert_size / 12), 1))
        start = int(np.random.randint(self.chr_pos_start, (self.chr_pos_end + 1)))
        left_end = start + self.read_length
        total_end = start + int(np.round(insert))
        right_start = total_end - self.read_length
        if total_end > self.chr_pos_end:
            # split read scenario or insert spanning split read scenario
            if left_end > self.chr_pos_end:
                # left read spanning split read scenario
                # left_read
                left_dntps = self.chr_pos_end - start
                right_dntps = self.read_length - left_dntps

                # the error could be here
                left_split_read = fastafile.fetch(self.chr, start, self.chr_pos_end)
                right_split_read = fastafile.fetch(self.chr, self.chr_pos_start, (self.chr_pos_start + right_dntps))
                left_read = left_split_read + right_split_read

                # right_read
                right_start = self.chr_pos_start + int(round(self.insert_size - left_dntps - self.read_length))
                right_read = fastafile.fetch(self.chr, right_start, (right_start + self.read_length))

                # assertion to check the error here

                common_id = "%s|%s|%s:%s-%s:%s|%s:%s|1|%s" % (
                self.read_number, self.chr, start, self.chr_pos_end, self.chr_pos_start, (self.chr_pos_start + right_dntps), right_start,
                (right_start + self.read_length), self.circle_id)




            else:
                if right_start > self.chr_pos_end:
                    # insert spanning split read scenario
                    left_read = fastafile.fetch(self.chr, start, (start + self.read_length))
                    right_start = self.chr_pos_start + (right_start - self.chr_pos_end)
                    right_read = fastafile.fetch(self.chr, right_start, (right_start + self.read_length))
                    common_id = "%s|%s|%s:%s|%s:%s|3|%s" % (
                        self.read_number, self.chr, start, (start + self.read_length), right_start, (right_start + self.read_length), self.circle_id)
                else:
                    # right split read scenario
                    assert right_start <= self.chr_pos_end
                    assert (right_start + self.read_length) > self.chr_pos_end
                    left_read = fastafile.fetch(self.chr, start, (start + self.read_length))

                    # compute right dntps
                    left_dntps = self.chr_pos_end - right_start
                    right_dntps = self.read_length - left_dntps
                    left_split_read = fastafile.fetch(self.chr, right_start, self.chr_pos_end)
                    right_split_read = fastafile.fetch(self.chr, self.chr_pos_start, (self.chr_pos_start + right_dntps))
                    right_read = left_split_read + right_split_read
                    common_id = "%s|%s|%s:%s|%s:%s-%s:%s|2|%s" % (
                        self.read_number,self.chr, start, (start + self.read_length), right_start, self.chr_pos_end, self.chr_pos_start,
                        (self.chr_pos_start +
                         right_dntps), self.circle_id)


        else:
            # non split read scenario
            left_read = fastafile.fetch(self.chr, start, (start + self.read_length))
            # correct right read start
            right_read = fastafile.fetch(self.chr, right_start, (right_start + self.read_length))
            common_id = "%s|%s|%s:%s|%s:%s|0|%s" % (
                self.read_number, self.chr, start, (start + self.read_length), right_start, (right_start + self.read_length), self.circle_id)

        return(right_read,left_read,common_id)



    def simulate_perfect_read(self,right_read,left_read,common_id):
        # put all together
        # unique identifiers for right and left reads
        right_read_id = "2:N:0:CGCTGTG"
        right_id = common_id + "  " + right_read_id
        left_read_id = "1:N:0:CGCTGTG"
        left_id = common_id + "  " + left_read_id
        quality = "I" * self.read_length
        # get the reverse complement of the right read
        right_read = Seq(right_read, generic_dna)
        right_read = right_read.reverse_complement()
        fastq_left = "@%s\n%s\n+\n%s\n" % (left_id, left_read, quality)
        fastq_right = "@%s\n%s\n+\n%s\n" % (right_id, right_read, quality)

        right_record = SeqIO.read(StringIO(fastq_right), "fastq")
        left_record = SeqIO.read(StringIO(fastq_left), "fastq")
        return (left_record, right_record)


    def simulate_read_with_errors(self,right_read, left_read, common_id):
        # put all together
        # unique identifiers for right and left reads
        right_read_id = "2:N:0:CGCTGTG"
        right_id = common_id + "space" + right_read_id
        left_read_id = "1:N:0:CGCTGTG"
        left_id = common_id + "space" + left_read_id

        # attemp to use art to simulate the quality scores and the error rate

        left_fasta = open("left_read.fa", "w")
        left_fasta.write(">" + left_id + "\n" + str(left_read) + "\n")
        # sim the read with art
        left_fasta.close()
        os.system("art_illumina -ss HS25 -nf 0 -i left_read.fa -l %s -f 1 -o left > output" % self.read_length)
        with open("left.fq", 'r') as left:
            left_read = left.read().replace('space', '   ').replace('1:N:0:CGCTGTG-1', '1:N:0:CGCTGTG')

        left_record = SeqIO.read(StringIO(left_read), "fastq")
        # get the reverse complement of the right read
        right_read = Seq(right_read, generic_dna)
        right_read = right_read.reverse_complement()

        right_fasta = open("right_read.fa", "w")
        right_fasta.write(">" + right_id + "\n" + str(right_read) + "\n")
        right_fasta.close()
        # sim the read with art
        os.system("art_illumina -ss HS25  -nf 0 -i right_read.fa -l %s -f 1 -o right > output" % self.read_length)
        with open("right.fq", 'r') as right:
            right_read = right.read().replace('space', '   ').replace('1:N:0:CGCTGTG-1', '2:N:0:CGCTGTG')

        right_record = SeqIO.read(StringIO(right_read), "fastq")

        return (left_record, right_record)








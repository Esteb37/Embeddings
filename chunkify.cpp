// Copy a file into N chunks of equal size using multiple cores.
// Compile for Windows ecosystem
// The last chunk may be smaller than the others.
// The chunks are named chunk1, chunk2, etc.
// The file to be chunkified is specified on the command line.
// The number of chunks is specified on the command line.
// Compile with: g++ -std=c++11 -o chunkify chunkify.cpp -lpthread
// Usage: chunkify.exe <filename> <number of chunks>

#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

using namespace std;

struct Chunk
{
    int chunkNumber;
    string name;
    size_t size;
    size_t offset;
};

void WriteChunk(const string &filename, const Chunk &chunk)
{
    // Create a copy of the in stream
    ifstream in(filename, ios::binary);

    in.seekg(chunk.offset);
    in.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    // Seek to the next newline character

    vector<char> buffer(chunk.size);
    in.read(buffer.data(), chunk.size);

    // Write in text format
    ofstream out(chunk.name);
    out.write(buffer.data(), chunk.size);
}

double run(string filename, int numChunks, int runi)
{
    cout << "Run: " << runi << " Chunks: " << numChunks << endl;

    auto start = chrono::high_resolution_clock::now();

    // Array of ifstream objects
    ifstream ifs(filename, ios::binary);
    if (!ifs)
    {
        cerr << "Could not open " << filename << endl;
        return 1;
    }
    // Create directory "files" if it doesn't exist, if it does, delete contents
    // Use Linux commands
    system("mkdir -p files");
    system("rm -f files/*");

    ifs.seekg(0, ios::end);
    size_t fileSize = ifs.tellg();
    ifs.seekg(0, ios::beg);

    vector<Chunk> chunks(numChunks);
    size_t chunkSize = fileSize / numChunks;
    size_t offset = 0;
    for (size_t i = 0; i < numChunks; ++i)
    {
        chunks[i].chunkNumber = i + 1;
        chunks[i].name = "files/chunk" + to_string(i + 1) + ".txt";
        chunks[i].size = chunkSize;
        chunks[i].offset = offset;
        offset += chunkSize;
    }
    chunks.back().size += fileSize % numChunks;

    vector<thread> threads;
    for (auto &chunk : chunks)
    {
        threads.emplace_back(WriteChunk, ref(filename), ref(chunk));
    }

    for (auto &t : threads)
    {
        t.join();
    }

    auto end = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::milliseconds>(end - start);

    // Cast duration to double
    return duration.count();
}

int main(int argc, char *argv[])
{

    double sum = 0;
    for (int i = 0; i < 10; i++)
    {
        sum += run("glove.42B.300d.txt", 100, i + 1);
    }

    cout << 100 << " - Average time: " << sum / 10 << " milliseconds" << endl;

    system("ls -l files | wc -l");
    system("du -sh files");

    sum = 0;

    for (int i = 0; i < 10; i++)
    {
        sum += run("glove.42B.300d.txt", 20, i + 1);
    }

    cout << 20 << " - Average time: " << sum / 10 << " milliseconds" << endl;

    system("ls -l files | wc -l");
    system("du -sh files");

    sum = 0;

    for (int i = 0; i < 10; i++)
    {
        sum += run("glove.42B.300d.txt", 500, i + 1);
    }

    cout << 500 << " - Average time: " << sum / 10 << " milliseconds" << endl;

    system("ls -l files | wc -l");
    system("du -sh files");

    sum = 0;

    for (int i = 0; i < 10; i++)
    {
        sum += run("glove.42B.300d.txt", 1000, i + 1);
    }

    cout << 1000 << " - Average time: " << sum / 10 << " milliseconds" << endl;

    system("ls -l files | wc -l");
    system("du -sh files");
}
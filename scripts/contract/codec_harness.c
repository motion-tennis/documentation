#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "pb_decode.h"
#include "pb_encode.h"
#include "motion.pb.h"
#include "contract_resources.h"

// Offline generated-codec fixture tool. No transport, simulation, or device code.
static uint8_t input_buffer[CONTRACT_FRAME_LIMIT];
static uint8_t output_buffer[CONTRACT_FRAME_LIMIT];
static motion_v03_Envelope envelope;

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--resources") == 0) {
        print_contract_resources();
        return 0;
    }
    if (argc != 3) {
        fprintf(stderr, "Usage: codec_harness INPUT OUTPUT | --resources\n");
        return 2;
    }
    FILE *input = fopen(argv[1], "rb");
    if (input == NULL) {
        perror("input");
        return 2;
    }
    size_t length = fread(input_buffer, 1, sizeof(input_buffer), input);
    int extra = fgetc(input);
    int read_error = ferror(input);
    fclose(input);
    if (read_error || extra != EOF) {
        fprintf(stderr, "Input exceeds the bounded frame or cannot be read\n");
        return 2;
    }
    memset(&envelope, 0, sizeof(envelope));
    pb_istream_t reader = pb_istream_from_buffer(input_buffer, length);
    if (!pb_decode(&reader, motion_v03_Envelope_fields, &envelope)) {
        fprintf(stderr, "Decode rejected: %s\n", PB_GET_ERROR(&reader));
        return 1;
    }
    pb_ostream_t writer = pb_ostream_from_buffer(output_buffer, sizeof(output_buffer));
    if (!pb_encode(&writer, motion_v03_Envelope_fields, &envelope)) {
        fprintf(stderr, "Encode rejected: %s\n", PB_GET_ERROR(&writer));
        return 1;
    }
    // A successful C string decode alone cannot detect an embedded NUL.
    // Exact canonical bytes also reject unknown fields and duplicate encodings.
    if (writer.bytes_written != length || memcmp(input_buffer, output_buffer, length) != 0) {
        fprintf(stderr, "Canonical wire check rejected changed or unknown content\n");
        return 1;
    }
    FILE *output = fopen(argv[2], "wb");
    if (output == NULL) {
        perror("output");
        return 2;
    }
    int failed = fwrite(output_buffer, 1, writer.bytes_written, output) != writer.bytes_written;
    failed |= fclose(output) != 0;
    if (failed) {
        fprintf(stderr, "Cannot write encoded output\n");
        return 2;
    }
    return 0;
}

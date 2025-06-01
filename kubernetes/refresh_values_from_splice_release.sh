#!/bin/bash

# Define source and destination directories
source_dir="$1"
dest_dir="$2"

# Check if directories are provided
if [ -z "$source_dir" ] || [ -z "$dest_dir" ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

# Check if directories exist
if [ ! -d "$source_dir" ]; then
    echo "Error: Source directory '$source_dir' does not exist"
    exit 1
fi
if [ ! -d "$dest_dir" ]; then
    echo "Error: Destination directory '$dest_dir' does not exist"
    exit 1
fi

# Check if diff command is available
if ! command -v diff &> /dev/null; then
    echo "Error: diff command not found"
    exit 1
fi

# Find all .yaml files in source directory
for source_file in "$source_dir"/*.yaml; do
    # Check if there are any .yaml files
    if [ ! -f "$source_file" ]; then
        echo "No .yaml files found in source directory"
        exit 0
    fi
    
    # Get the basename of the file
    filename=$(basename "$source_file")
    
    # Calculate MD5 checksum of source file
    source_md5=$(md5sum "$source_file" | cut -d' ' -f1)
    
    # Find matching files in destination directory (including subdirectories)
    while IFS= read -r dest_file; do
        if [ -f "$dest_file" ]; then
            # Calculate MD5 checksum of destination file
            dest_md5=$(md5sum "$dest_file" | cut -d' ' -f1)
            
            # Compare checksums
            if [ "$source_md5" != "$dest_md5" ]; then
                echo "Updating $dest_file (checksums differ)"
                echo "Changes:"
                diff -u "$dest_file" "$source_file" | sed 's/^/  /'
                cp "$source_file" "$dest_file"
            else
                echo "Skipping $dest_file (identical checksum)"
            fi
        fi
    done < <(find "$dest_dir" -type f -name "$filename")
done

echo "Update complete"

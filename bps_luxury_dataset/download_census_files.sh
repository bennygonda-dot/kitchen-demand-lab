#!/bin/bash
# Census BPS Data Downloader
# Downloads CBSA/Metro building permits files from Census Bureau

set -e

# Create input directory
mkdir -p input_data/historical
mkdir -p input_data/modern

echo "=========================================="
echo "Census BPS CBSA Data Downloader"
echo "=========================================="
echo ""
echo "This script will download Census Bureau Building Permits Survey"
echo "CBSA/Metro files from 1995 to present."
echo ""
echo "NOTE: Census Bureau may block automated downloads."
echo "If this script fails, you'll need to download files manually"
echo "from your browser and place them in input_data/ folders."
echo ""
read -p "Press Enter to start downloading or Ctrl+C to cancel..."

# Download modern CBSA Excel files (2019-11 to present)
echo ""
echo "Downloading modern CBSA files (2019-11 to present)..."
echo "------------------------------------------------------"

for year in {2019..2025}; do
    for month in {1..12}; do
        # Skip months before Nov 2019
        if [ $year -eq 2019 ] && [ $month -lt 11 ]; then
            continue
        fi

        # Skip future months
        if [ $year -eq 2025 ] && [ $month -gt 10 ]; then
            continue
        fi

        month_padded=$(printf "%02d" $month)
        filename="cbsa${year}${month_padded}.xlsx"
        url="https://www2.census.gov/econ/bps/CBSA/${filename}"

        echo -n "  ${year}-${month_padded}... "

        if curl -f -s -S --connect-timeout 10 -o "input_data/modern/${filename}" "${url}" 2>/dev/null; then
            # Check if file is actually Excel (not "Access denied" text)
            if file "input_data/modern/${filename}" | grep -q "Excel\|Zip"; then
                echo "✓"
            else
                echo "✗ (blocked)"
                rm "input_data/modern/${filename}"
            fi
        else
            echo "✗ (not found)"
        fi

        sleep 0.5  # Be nice to Census servers
    done
done

# Download historical Metro text files (1995-2019-10)
echo ""
echo "Downloading historical Metro files (1995-2019-10)..."
echo "------------------------------------------------------"

for year in {1995..2019}; do
    for month in {1..12}; do
        # Skip months after Oct 2019
        if [ $year -eq 2019 ] && [ $month -gt 10 ]; then
            continue
        fi

        month_padded=$(printf "%02d" $month)
        year_short=$(printf "%02d" $((year % 100)))

        # Try different filename patterns
        for filename in "ma${year}${month_padded}t.txt" "ma${year_short}${month_padded}t.txt"; do
            url="https://www2.census.gov/econ/bps/Metro/${filename}"

            echo -n "  ${year}-${month_padded} (${filename})... "

            if curl -f -s -S --connect-timeout 10 -o "input_data/historical/${filename}" "${url}" 2>/dev/null; then
                # Check if file is actually text data (not "Access denied")
                if [ -s "input_data/historical/${filename}" ] && ! grep -q "Access denied" "input_data/historical/${filename}"; then
                    echo "✓"
                    break  # Found it, don't try other pattern
                else
                    echo "✗ (blocked/empty)"
                    rm "input_data/historical/${filename}"
                fi
            else
                echo "✗ (not found)"
            fi
        done

        sleep 0.5
    done
done

echo ""
echo "=========================================="
echo "Download Summary"
echo "=========================================="
echo "Modern files downloaded: $(ls -1 input_data/modern/*.xlsx 2>/dev/null | wc -l)"
echo "Historical files downloaded: $(ls -1 input_data/historical/*.txt 2>/dev/null | wc -l)"
echo ""

if [ $(ls -1 input_data/modern/*.xlsx 2>/dev/null | wc -l) -eq 0 ] && [ $(ls -1 input_data/historical/*.txt 2>/dev/null | wc -l) -eq 0 ]; then
    echo "⚠️  NO FILES DOWNLOADED - Census Bureau is blocking automated access"
    echo ""
    echo "MANUAL DOWNLOAD REQUIRED:"
    echo "1. Open your web browser"
    echo "2. Visit: https://www2.census.gov/econ/bps/CBSA/"
    echo "3. Download files: cbsa201911.xlsx through cbsa202410.xlsx"
    echo "4. Save them to: $(pwd)/input_data/modern/"
    echo ""
    echo "5. Visit: https://www2.census.gov/econ/bps/Metro/"
    echo "6. Download files: ma*.txt (all files from 1995-2019)"
    echo "7. Save them to: $(pwd)/input_data/historical/"
else
    echo "✓ Some files downloaded successfully!"
    echo "You can now run: python make_luxury_permits_dataset.py"
fi

echo ""

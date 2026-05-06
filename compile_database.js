const fs = require('fs');
const path = require('path');
const officeParser = require('officeparser');

// Define directories
const ishDir = path.join(__dirname, 'Ish');
const outputDir = path.join(__dirname, 'data');
const outputFile = path.join(outputDir, 'crops.json');

// Ensure data directory exists
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
}

// Map of standard folder names to clean Uzbek crop category names
const cropCategoryMap = {
    'Bodring': 'Bodring',
    'Bug\'doy': 'Bug\'doy',
    'Kartoshka': 'Kartoshka',
    'Mikro\'kokat': 'Mikroko\'katlar',
    'Pamidor': 'Pomidor',
    'Paxta': 'Paxta',
    'Piyoz': 'Piyoz',
    'Tarvuz': 'Tarvuz',
    'Turli ekinlar': 'Turli ekinlar'
};

async function compileCropsDatabase() {
    console.log("🚀 Qishloq xo'jaligi ma'lumotlar bazasini tuzish boshlandi...");
    
    if (!fs.existsSync(ishDir)) {
        console.error(`Xatolik: 'Ish' papkasi topilmadi!`);
        return;
    }

    const compiledData = [];
    const categories = fs.readdirSync(ishDir);

    for (const folderName of categories) {
        const folderPath = path.join(ishDir, folderName);
        
        // Skip files, only process crop folders
        if (!fs.statSync(folderPath).isDirectory()) {
            continue;
        }

        const cleanCategory = cropCategoryMap[folderName] || folderName;
        console.log(`\n📁 Bo'lim: [${cleanCategory}] parsing qilinmoqda...`);

        const files = fs.readdirSync(folderPath);
        const docxFiles = files.filter(f => f.endsWith('.docx') && !f.startsWith('~$')); // Exclude temp word files

        for (const fileName of docxFiles) {
            const filePath = path.join(folderPath, fileName);
            const varietyName = fileName.replace('_qr.docx', '').replace('.docx', '').replace('_', ' ');
            
            console.log(`  📄 Fayl: ${fileName} -> Nav nomi: "${varietyName}"`);

            try {
                // Parse .docx content
                const dataObj = await officeParser.parseOffice(filePath);
                const fullText = dataObj.toText().trim();
                
                if (!fullText) {
                    console.log(`   ⚠️ Diqqat: fayl matni bo'sh.`);
                    continue;
                }

                // Add to database
                compiledData.push({
                    name: varietyName,
                    category: cleanCategory,
                    filename: fileName,
                    content: fullText
                });

            } catch (err) {
                console.error(`   ❌ Faylni o'qishda xatolik [${fileName}]:`, err.message);
            }
        }
    }

    // Save compiled database
    console.log(`\n💾 Jami ${compiledData.length} ta nav ma'lumotlari muvaffaqiyatli yuklandi.`);
    fs.writeFileSync(outputFile, JSON.stringify(compiledData, null, 2), 'utf-8');
    console.log(`✅ Ma'lumotlar bazasi saqlandi: ${outputFile} (${Math.round(fs.statSync(outputFile).size / 1024)} KB)`);
}

compileCropsDatabase();

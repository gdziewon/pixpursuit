import Image from "next/image";

export async function generateStaticParams() {
    const res = await fetch('https://api.slingacademy.com/v1/sample-data/photos');

    const data = await res.json();

    return data.photos.map(photo => ({
        id: photo.id.toString()
    }));
}

export async function getPhoto(id){
    const res = await fetch(`https://api.slingacademy.com/v1/sample-data/photos/${id}`, {
        next: {
            revalidate: 0
        }
    });

    const data = await res.json();
    return data.photo;
}

export default function Photo( { params}) {
    const photo = getPhoto(params.id);

    return (
        <>
            <div className="container mx-auto px-4 py-16">
                <h2 className="text-4xl font-bold mb-8">Photo</h2>
                <div className="bg-white rounded shadow overflow-hidden">
                    <Image src={photo.url} alt={photo.title} width={640} height={480}/>
                    <div className="p-4">
                        <h3 className="text-xl font-semibold mb-2">{photo.title}</h3>
                        <p className="text-gray-500">{photo.description}</p>
                    </div>
                </div>
            </div>
        </>
    )
};
import os
import exifread
import folium
from folium.plugins import MarkerCluster

def get_exif_data(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
        lat = tags.get('GPS GPSLatitude')
        lon = tags.get('GPS GPSLongitude')
        date = tags.get('EXIF DateTimeOriginal')
        
        if lat and lon and date:
            lat = [float(x.num) / float(x.den) for x in lat.values]
            lon = [float(x.num) / float(x.den) for x in lon.values]
            latitude = lat[0] + lat[1] / 60 + lat[2] / 3600
            longitude = lon[0] + lon[1] / 60 + lon[2] / 3600
            if tags['GPS GPSLatitudeRef'].values[0] != 'N':
                latitude = -latitude
            if tags['GPS GPSLongitudeRef'].values[0] != 'E':
                longitude = -longitude
            return {
                'path': image_path,
                'latitude': latitude,
                'longitude': longitude,
                'datetime': str(date)
            }
    return None


def main(photo_dir):
    # ディレクトリ内の全ての写真を取得
    photo_files = [os.path.join(photo_dir, f) for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg'))]

    # EXIF情報を取得
    photo_data = [get_exif_data(photo) for photo in photo_files]
    photo_data = [data for data in photo_data if data]

    # 地図の作成
    map_center = [photo_data[0]['latitude'], photo_data[0]['longitude']]
    map_ = folium.Map(location=map_center, zoom_start=12)

    # マーカークラスタを追加
    marker_cluster = MarkerCluster().add_to(map_)

    # 写真の位置情報を地図上にマーカーとして追加
    for photo in photo_data:
        # 画像の絶対パスを相対パスに変換
        photo_path = os.path.relpath(photo['path'], photo_dir)
        popup_html = f"""
        <div>
            <img src='{photo_path}' width='150'><br>
            {photo['datetime']}
        </div>
        """
        folium.Marker(
            location=[photo['latitude'], photo['longitude']],
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(marker_cluster)

    # 地図をHTMLファイルに保存
    map_.save(f"{photo_dir}/photo_map.html")
    print("地図を 'photo_map.html' に保存しました。")


if __name__=='__main__':
    photo_dir = "./data/20240608"
    main(photo_dir)

